import argparse
import hashlib
import os
import platform
import shlex
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path


BINUTILS_SHA256 = 'fd7d227c0dd15cf5448385e56b8ad8313cd491839834b57c0c086ac7b7819a15'
BINUTILS_URLS = (
    'https://ftp.gnu.org/gnu/binutils/binutils-2.10.tar.gz',
    'https://mirrors.kernel.org/gnu/binutils/binutils-2.10.tar.gz',
    'https://mirrors.ocf.berkeley.edu/gnu/binutils/binutils-2.10.tar.gz',
    'https://mirror.csclub.uwaterloo.ca/gnu/binutils/binutils-2.10.tar.gz',
)
AGBCC_REVISION = 'da598c1d918402c42c0c0d7128ba14567f3175e9'
AGBCC_SHA256 = 'f69ae187a6133b1d353a01a86c1da92a9e38df06c6d3e08e2ae360ea051c1b60'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--prefix', type=Path)
    parser.add_argument('--build-dir', type=Path)
    parser.add_argument('--jobs', type=int, default=min(os.cpu_count() or 1, 8))
    args = parser.parse_args()
    root = args.root.resolve()
    prefix = (args.prefix or root / 'tools/legacy').resolve()
    work = (args.build_dir or root / 'build/toolchain').resolve()
    compiler = root / 'tools/agbcc/bin/old_agbcc.exe'
    if not compiler.is_file():
        parser.error('install agbcc before setting up the legacy toolchain')
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    work.mkdir(parents=True, exist_ok=True)
    log_path = work / 'setup.log'
    env = os.environ.copy()
    env.update(CC='cc -std=gnu89 -Wno-implicit-function-declaration -Wno-int-conversion', CFLAGS='-O2',
               lt_cv_sys_max_cmd_len=str((os.sysconf('SC_ARG_MAX') * 3 // 4) if hasattr(os, 'sysconf') else 32768))

    def run(command, directory=work):
        command = list(map(str, command))
        if command[0].endswith('/configure') or command[0].endswith('\\configure'):
            command.insert(0, 'bash')
        with log_path.open('a') as log:
            print(shlex.join(command), file=log, flush=True)
            subprocess.run(command, cwd=directory, env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)

    def fetch(name, urls, digest):
        archive = work / name
        if not archive.exists():
            temporary = archive.with_suffix('.download')
            failures = []
            for url in [urls] if isinstance(urls, str) else urls:
                try:
                    with urllib.request.urlopen(url, timeout=60) as response, temporary.open('wb') as output:
                        shutil.copyfileobj(response, output)
                except OSError as error:
                    failures.append(f'{url}: {error}')
                    continue
                if hashlib.sha256(temporary.read_bytes()).hexdigest() == digest:
                    temporary.replace(archive)
                    break
                failures.append(f'{url}: SHA-256 differs from the pinned source')
            else:
                raise RuntimeError(f'could not download {name}:\n' + '\n'.join(failures))
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError(f'{archive}: SHA-256 differs from the pinned source')
        return archive

    def replace(path, before, after):
        text = path.read_text()
        if before in text:
            path.write_text(text.replace(before, after))
        elif after not in text:
            raise ValueError(f'{path}: expected source for host compatibility edit is absent')

    print('Building the binutils 2.10 assembler and linker', flush=True)
    archive = fetch('binutils-2.10.tar.gz', BINUTILS_URLS, BINUTILS_SHA256)
    source = work / 'binutils-2.10'
    if not source.exists():
        run(['tar', '-xzf', archive, '-C', work])
    replace(source / 'config.sub', '| arm-* | c[123]*', '| arm-* | aarch64-* | x86_64-* | c[123]*')
    replace(source / 'config.sub', '| -mingw32* | -linux-gnu*', '| -mingw32* | -darwin* | -linux-gnu*')
    machine = {'arm64': 'aarch64', 'AMD64': 'x86_64'}.get(platform.machine(), platform.machine())
    if platform.system() == 'Darwin':
        host = machine + '-apple-darwin'
        replace(source / 'libiberty/strerror.c', 'extern int sys_nerr;', 'extern const int sys_nerr;')
    elif platform.system() == 'Linux':
        host = machine + '-pc-linux-gnu'
    elif platform.system() == 'Windows':
        host = machine + '-pc-mingw32'
    else:
        parser.error('unsupported host operating system')
    build = work / 'binutils-build'
    build.mkdir(exist_ok=True)
    run(['bash', '../binutils-2.10/configure', '--host=' + host, '--build=' + host,
         '--target=arm-elf', '--disable-nls', '--disable-shared'], build)
    run(['make', '-j' + str(args.jobs), 'all-gas', 'all-ld'], build)
    (prefix / 'bin').mkdir(parents=True, exist_ok=True)
    assembler = prefix / 'bin/arm-elf-as'
    shutil.copy2(build / 'gas/as-new.exe', assembler)
    shutil.copy2(build / 'ld/ld-new.exe', prefix / 'bin/arm-elf-ld')

    print('Rebuilding the runtime libraries for the legacy software-FP ABI', flush=True)
    archive = fetch('agbcc-' + AGBCC_REVISION + '.tar.gz',
                    'https://codeload.github.com/pret/agbcc/tar.gz/' + AGBCC_REVISION,
                    AGBCC_SHA256)
    agbcc = work / ('agbcc-' + AGBCC_REVISION)
    if not agbcc.exists():
        run(['tar', '-xzf', archive, '-C', work])
    with tempfile.TemporaryDirectory(prefix='runtime-', dir=work) as directory:
        libraries = Path(directory)
        for name in ('libgcc', 'libc', 'ginclude'):
            shutil.copytree(agbcc / name, libraries / name)
        (libraries / 'old_agbcc').symlink_to(compiler)
        for name in ('libgcc', 'libc'):
            replace(libraries / name / 'Makefile', '-mcpu=arm7tdmi', '-marm7tdmi')
            run(['make', '-B', '-j' + str(args.jobs), 'SHELL=bash -e -o pipefail',
                 'AS=' + shlex.quote(str(assembler)) + ' -mno-fpu',
                 'CPP=arm-none-eabi-cpp'], libraries / name)
        (prefix / 'lib').mkdir(exist_ok=True)
        for name in ('libgcc', 'libc'):
            shutil.copy2(libraries / name / (name + '.a'), prefix / 'lib' / (name + '.a'))
    print('Legacy assembler, linker and libraries installed in ' + str(prefix), flush=True)


if __name__ == '__main__':
    main()
