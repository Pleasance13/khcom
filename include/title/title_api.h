#ifndef GUARD_TITLE_API_H
#define GUARD_TITLE_API_H

#include "types.h"

enum TitleMenuChoice {
    TITLE_MENU_NEW_GAME,
    TITLE_MENU_CONTINUE,
    TITLE_MENU_LINK_BATTLE,
    TITLE_MENU_RESUME,
    TITLE_MENU_NEW_GAME_SORA,
    TITLE_MENU_NEW_GAME_RIKU,
    TITLE_MENU_ROGUE_MODE
};

void TitleCopyToPaletteBuffer(u16 slot, void* src, u16 size);
void TitleLoadPaletteBuffer();
u8 IsTitleObjSlideDone();

#endif
