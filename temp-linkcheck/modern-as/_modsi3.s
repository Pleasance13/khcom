# 0 "../../tools/agbcc/libgcc/lib1thumb.asm"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "../../tools/agbcc/libgcc/lib1thumb.asm"
@ libgcc1 routines for ARM cpu.
@ Division routines, written by Richard Earnshaw, (rearnsha@armltd.co.uk)
# 36 "../../tools/agbcc/libgcc/lib1thumb.asm"
 .code 16
# 45 "../../tools/agbcc/libgcc/lib1thumb.asm"
work .req r4 @ XXXX is this safe ?
# 423 "../../tools/agbcc/libgcc/lib1thumb.asm"
dividend .req r0
divisor .req r1
overdone .req r2
curbit .req r3

 .text
 .globl __modsi3
 .type __modsi3,function
 .align 2, 0
 .thumb_func
__modsi3:
 mov curbit, #1
 cmp divisor, #0
 beq Ldiv0
 Bpl Over1
 neg divisor, divisor @ Loops below use unsigned.
Over1:
 push { work }
 @ Need to save the sign of the dividend, unfortunately, we need
 @ ip later on. Must do this after saving the original value of
 @ the work register, because we will pop this value off first.
 push { dividend }
 cmp dividend, #0
 Bpl Over2
 neg dividend, dividend
Over2:
 cmp dividend, divisor
 bcc Lgot_result
 mov work, #1
 lsl work, #28
Loop1:
 @ Unless the divisor is very big, shift it up in multiples of
 @ four bits, since this is the amount of unwinding in the main
 @ division loop. Continue shifting until the divisor is
 @ larger than the dividend.
 cmp divisor, work
 bcs Lbignum
 cmp divisor, dividend
 bcs Lbignum
 lsl divisor, #4
 lsl curbit, #4
 b Loop1

Lbignum:
 @ Set work to 0x80000000
 lsl work, #3
Loop2:
 @ For very big divisors, we must shift it a bit at a time, or
 @ we will be in danger of overflowing.
 cmp divisor, work
 bcs Loop3
 cmp divisor, dividend
 bcs Loop3
 lsl divisor, #1
 lsl curbit, #1
 b Loop2

Loop3:
 @ Test for possible subtractions. On the final pass, this may
 @ subtract too much from the dividend, so keep track of which
 @ subtractions are done, we can fix them up afterwards...
 mov overdone, #0
 cmp dividend, divisor
 bcc Over3
 sub dividend, dividend, divisor
Over3:
 lsr work, divisor, #1
 cmp dividend, work
 bcc Over4
 sub dividend, dividend, work
 mov ip, curbit
 mov work, #1
 ror curbit, work
 orr overdone, curbit
 mov curbit, ip
Over4:
 lsr work, divisor, #2
 cmp dividend, work
 bcc Over5
 sub dividend, dividend, work
 mov ip, curbit
 mov work, #2
 ror curbit, work
 orr overdone, curbit
 mov curbit, ip
Over5:
 lsr work, divisor, #3
 cmp dividend, work
 bcc Over6
 sub dividend, dividend, work
 mov ip, curbit
 mov work, #3
 ror curbit, work
 orr overdone, curbit
 mov curbit, ip
Over6:
 mov ip, curbit
 cmp dividend, #0 @ Early termination?
 beq Over7
 lsr curbit, #4 @ No, any more bits to do?
 beq Over7
 lsr divisor, #4
 b Loop3

Over7:
 @ Any subtractions that we should not have done will be recorded in
 @ the top three bits of "overdone". Exactly which were not needed
 @ are governed by the position of the bit, stored in ip.
 @ If we terminated early, because dividend became zero,
 @ then none of the below will match, since the bit in ip will not be
 @ in the bottom nibble.
 mov work, #0xe
 lsl work, #28
 and overdone, work
 beq Lgot_result

 mov curbit, ip
 mov work, #3
 ror curbit, work
 tst overdone, curbit
 beq Over8
 lsr work, divisor, #3
 add dividend, dividend, work
Over8:
 mov curbit, ip
 mov work, #2
 ror curbit, work
 tst overdone, curbit
 beq Over9
 lsr work, divisor, #2
 add dividend, dividend, work
Over9:
 mov curbit, ip
 mov work, #1
 ror curbit, work
 tst overdone, curbit
 beq Lgot_result
 lsr work, divisor, #1
 add dividend, dividend, work
Lgot_result:
 pop { work }
 cmp work, #0
 bpl Over10
 neg dividend, dividend
Over10:
 pop { work }
 mov pc, lr

Ldiv0:
 push { lr }
 bl __div0
 mov r0, #0 @ about as wrong as it could be
 pop { pc }

 .size __modsi3, . - __modsi3
.text
	.align	2, 0
