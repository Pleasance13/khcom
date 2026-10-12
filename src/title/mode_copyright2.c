/**
 * mode_copyright2.c
 * Second Copyright Screen
 */

#include "registration_data.h"
#include "copyright_screens.h"
#include "fade.h"
#include "display.h"
#include "mode.h"
#include "types.h"
#include "gba/keys.h"
#include "key.h"

static u16 sCopyright2Timer;

void mode_copyright2_0(s32 arg) {
    SetBgMode0();
    SetupBg(0, 0, 0x1F, 0);
    SetBgPriority(0, 3);
    LoadBgTiles(0, gCopyright2Tiles, sizeof(gCopyright2Tiles));
    LoadBgPalette(0, gCopyright2Palette, sizeof(gCopyright2Palette));
    LoadBgMap(0, gCopyright2Map, sizeof(gCopyright2Map));

    if (arg == 0) {
        FadeStartIn(FADE_MODE_BLACK, 0x43);
    } else {
        FadeStartIn(FADE_MODE_WHITE, 0x43);
    }

    sCopyright2Timer = 60;
}


void mode_copyright2_1() {
    if (GetKeysPressed() & (A_BUTTON | START_BUTTON)) {
        ModeRequest(&gModeTitle, 0);
        return;
    }

    if (!FadeIsActive()) {
        if (sCopyright2Timer != 0) {
            if (--sCopyright2Timer == 0) {
                FadeStartOut(FADE_MODE_BLACK, 0x43);
            }
        } else {
            ModeRequest(&gModeTitle, 0);
        }
    }
}

void mode_copyright2_2() {
}

Mode gModeCopyright2 = {
    "mode_copyright2",
    mode_copyright2_0,
    mode_copyright2_1,
    mode_copyright2_2,
};
