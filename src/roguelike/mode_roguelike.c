#include "display.h"
#include "fade.h"
#include "gba/keys.h"
#include "key.h"
#include "mode.h"
#include "pallet.h"
#include "registration_data.h"
#include "sprites_mode_debug.h"
#include "debug_text.h"
#include "debug/mode_chkbtl.h"
#include "types.h"

static u8 sRewardChoice;
static u8 sRewardConfirmed;

static const char* sRewardNames[] = {
    "\x82\x60\x82\x73\x82\x73\x82\x60\x82\x62\x81\x40\x82\x62\x82\x60\x82\x71\x82\x63",
    "\x82\x6d\x82\x60\x82\x66\x82\x68\x82\x62\x81\x40\x82\x62\x82\x60\x82\x71\x82\x63",
    "\x82\x64\x82\x6d\x82\x64\x82\x6d\x82\x78\x81\x40\x82\x62\x82\x60\x82\x71\x82\x63",
};

void mode_roguelike_0(u32 arg)
{
    FadeStartIn(FADE_MODE_BLACK, 16);

    SetBgMode0();
    SetupBg(0, 0, 0x0F, 0);
    EnableBg(0);

    DebugTextInit(0, 0x5400, 0x500);
    DebugTextLoadPalette(0, gWhitePalette, sizeof(gWhitePalette), 0x0F);

    SetupBg(1, 1, 0x0C, 8);
    LoadBgTiles(1, gDebugCheckerBgTiles, sizeof(gDebugCheckerBgTiles));
    LoadBgPalette(1, gDebugCheckerBgPalette, sizeof(gDebugCheckerBgPalette));
    LoadBgMap(1, gDebugCheckerBgMap, sizeof(gDebugCheckerBgMap));
    EnableBg(1);

    sRewardChoice = 0;
    sRewardConfirmed = FALSE;
}

void mode_roguelike_1(void)
{
    if (!sRewardConfirmed) {
        if (GetKeysRepeat() & DPAD_LEFT) {
            sRewardChoice = (sRewardChoice + 2) % 3;
        }

        if (GetKeysRepeat() & DPAD_RIGHT) {
            sRewardChoice = (sRewardChoice + 1) % 3;
        }

        if (GetKeysPressed() & A_BUTTON) {
            sRewardConfirmed = TRUE;
        }
    }

    if (GetKeysPressed() & B_BUTTON) {
        ModeRequest(&gModeDebug, 0);
        return;
    }

    DebugTextPrint(16, 16, 2,
        "\x82\x71\x82\x6e\x82\x66\x82\x74\x82\x6b\x82\x68\x82\x6a\x82\x64\x81\x40\x82\x73\x82\x64\x82\x72\x82\x73");

    DebugTextPrint(16, 40, 2,
        "\x82\x62\x82\x67\x82\x6e\x82\x6e\x82\x72\x82\x64\x81\x40\x82\x60\x81\x40\x82\x71\x82\x64\x82\x76\x82\x60\x82\x71\x82\x63");

    DebugTextPrint(16, 64, 2, sRewardNames[sRewardChoice]);

    if (sRewardConfirmed) {
        DebugTextPrint(16, 96, 2,
            "\x82\x72\x82\x64\x82\x6b\x82\x64\x82\x62\x82\x73\x82\x64\x82\x63\x81\x49");
    } else {
        DebugTextPrint(16, 96, 2,
            "\x82\x6b\x82\x64\x82\x65\x82\x73\x81\x40\x82\x6e\x82\x71\x81\x40\x82\x71\x82\x68\x82\x66\x82\x67\x82\x73");

        DebugTextPrint(16, 120, 2,
            "\x82\x60\x81\x40\x82\x73\x82\x6e\x81\x40\x82\x62\x82\x6e\x82\x6d\x82\x65\x82\x68\x82\x71\x82\x6d");

        DebugTextPrint(16, 144, 2,
            "\x82\x61\x81\x40\x82\x73\x82\x6e\x81\x40\x82\x61\x82\x60\x82\x62\x82\x6a");
    }

    DebugTextDraw(0);
    DebugTextClear();
}

void mode_roguelike_2(void)
{
    DebugTextDestroy();
}

Mode gModeRoguelike = {
    "mode_roguelike",
    (ModeInitFunc)mode_roguelike_0,
    mode_roguelike_1,
    mode_roguelike_2
};