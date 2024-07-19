#include <X11/XF86keysym.h>

static int showsystray                   = 1;         /* 是否显示托盘栏 */
static const int newclientathead         = 0;         /* 定义新窗口在栈顶还是栈底 */
static const int managetransientwin      = 1;         /* 是否管理临时窗口 */
static const unsigned int borderpx       = 3;         /* 窗口边框大小 */
static const unsigned int systraypinning = 1;         /* 托盘跟随的显示器 0代表不指定显示器 */
static const unsigned int systrayspacing = 0;         /* 托盘间距 */
static const unsigned int systrayspadding = 0;        /* 托盘和状态栏的间隙 */
static int gappi                          = 5;        /* 窗口与窗口 缝隙大小 */
static int gappo                          = 5;        /* 窗口与边缘 缝隙大小 */
// static int gappi                         = 10;        /* 窗口与窗口 缝隙大小 */
// static int gappo                         = 10;        /* 窗口与边缘 缝隙大小 */
static const int _gappo                  = 12;        /* 窗口与窗口 缝隙大小 不可变 用于恢复时的默认值 */
static const int _gappi                  = 12;        /* 窗口与边缘 缝隙大小 不可变 用于恢复时的默认值 */
static const int vertpad                 = 0;         /* vertical padding of bar */
static const int sidepad                 = 5;         /* horizontal padding of bar */
static const int overviewgappi           = 12;        /* overview时 窗口与边缘 缝隙大小 */
static const int overviewgappo           = 12;        /* overview时 窗口与窗口 缝隙大小 */
static const int showbar                 = 1;         /* 是否显示状态栏 */
static const int topbar                  = 0;         /* 指定状态栏位置 0底部 1顶部 */
static const float mfact                 = 0.65;      /* 主工作区 大小比例 */
static const int   nmaster               = 1;         /* 主工作区 窗口数量 */
static const unsigned int snap           = 5;         /* 边缘依附宽度 */
static const unsigned int baralpha       = 0xa0;      /* 状态栏透明度 */
static const unsigned int borderalpha    = 0xff;      /* 边框透明度 */
static const char *fonts[]               = { "Maple Mono NF:style=medium:size=13", "Ubuntu Nerd Font Mono:size=13" };
/*
static const char black[]       = "#21222C";
static const char white[]       = "#f8f8f2";
static const char gray2[]       = "#282a36"; // unfocused window border
static const char gray3[]       = "#44475a";
static const char gray4[]       = "#282a36";
static const char blue[]        = "#bd93f9";  // focused window border
static const char green[]       = "#50fa7b";
static const char red[]         = "#ff5555";
static const char orange[]      = "#ffb86c";
static const char yellow[]      = "#f1fa8c";
static const char pink[]        = "#ff79c6";
static const char col_borderbar[]  = "#21222c"; // inner border
*/

static const char *colors[][3]           = {          /* 颜色设置 ColFg, ColBg, ColBorder */ 
    [SchemeNorm] = { "#999999", "#21222C", "#21222C" },
    [SchemeSel] = { "#282a36", "#bd93f9", "#bd93f9" },
    [SchemeSelGlobal] = { "#f1fa8c", "#21222C", "#f1fa8c" },
    [SchemeHid] = { "#304050", "#21222c", NULL },
    [SchemeSystray] = { NULL, "#21222c", NULL },
    [SchemeUnderline] = { "#ff556c", "#ffffff", NULL }, 
    [SchemeNormTag] = { "#bbbbbb", "#21222c", NULL },
    [SchemeSelTag] = { "#ff5555", "#21222C", NULL },
    [SchemeBarEmpty] = { NULL, "#21222c", NULL },
};
static const unsigned int alphas[][3]    = {          /* 透明度设置 ColFg, ColBg, ColBorder */ 
    [SchemeNorm] = { OPAQUE, baralpha, borderalpha }, 
    [SchemeSel] = { OPAQUE, baralpha, borderalpha },
    [SchemeSelGlobal] = { OPAQUE, baralpha, borderalpha },
    [SchemeNormTag] = { OPAQUE, baralpha, borderalpha }, 
    [SchemeSelTag] = { OPAQUE, baralpha, borderalpha },
    [SchemeBarEmpty] = { 0, 0, 0 },
    [SchemeStatusText] = { OPAQUE, 0x88, 0 },
};

/* 自定义脚本位置 */
static const char *autostartscript = "$DWM/autostart.sh";
static const char *statusbarscript = "$DWM/statusbar/statusbar.sh";

/* 自定义 scratchpad instance */
static const char scratchpadname[] = "scratchpad";

/* 自定义tag名称 */
/* 自定义特定实例的显示状态 */
static const char *tags[] = { 
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "", //tag 9: 放一些聊天的软件 super 0 
};

/* 自定义窗口显示规则 */
/* class instance title 主要用于定位窗口适合哪个规则 */
/* tags mask 定义符合该规则的窗口的tag 0 表示当前tag */
/* isfloating 定义符合该规则的窗口是否浮动 */
/* isglobal 定义符合该规则的窗口是否全局浮动 */
/* isnoborder 定义符合该规则的窗口是否无边框 */
/* monitor 定义符合该规则的窗口显示在哪个显示器上 -1 为当前屏幕 */
/* floatposition 定义符合该规则的窗口显示的位置 0 中间，1到9分别为9宫格位置，例如1左上，9右下，3右上 */
static const Rule rules[] = {
    /* class                 instance              title             tags mask     isfloating  isglobal    isnoborder monitor floatposition */
    /** 优先级高 越在上面优先度越高 */
    { NULL,                  NULL,                "保存文件",        0,            1,          0,          0,        -1,      0}, // 浏览器保存文件      浮动
    { NULL,                  NULL,                "图片查看器",      0,            1,          0,          0,        -1,      0}, // qq图片查看器        浮动
    { NULL,                  NULL,                "图片查看",        0,            1,          0,          0,        -1,      0}, // 微信图片查看器      浮动
    { NULL,                  NULL,                "图片预览",        0,            1,          0,          0,        -1,      0}, // 企业微信图片查看器  浮动
    { NULL,                  NULL,                "Media viewer",   0,            1,          0,          0,        -1,      0}, // tg图片查看器        浮动

    /** 普通优先度 */
    { NULL,                 "qq",                  NULL,             1 << 8,       0,          0,          1,        -1,      0}, // qq         tag -> ﬄ 无边框
    {"scratchpad",          "scratchpad",         "scratchpad",      TAGMASK,      1,          1,          0,        -1,      8}, // scratchpad          浮动、全局、无边框 屏幕顶部*/
    /*{"obs",                  NULL,                 NULL,             1 << 3,       0,          0,          0,        -1,      0}, // obs        tag -> 󰕧*/
    /*{"chrome",               NULL,                 NULL,             1 << 4,       0,          0,          0,        -1,      0}, // chrome     tag -> */
    /*{"Chromium",             NULL,                 NULL,             1 << 4,       0,          0,          0,        -1,      0}, // Chromium   tag -> */
    /*{"music",                NULL,                 NULL,             1 << 5,       1,          0,          1,        -1,      0}, // music      tag ->  浮动、无边框*/
    /*{ NULL,                 "wechat.exe",          NULL,             1 << 7,       0,          0,          1,        -1,      0}, // wechat     tag -> ﬐ 无边框*/
    /*{ NULL,                 "wxwork.exe",          NULL,             1 << 8,       0,          0,          1,        -1,      0}, // workwechat tag ->  无边框*/
    /*{"Vncviewer",            NULL,                 NULL,             0,            1,          0,          1,        -1,      2}, // Vncviewer           浮动、无边框 屏幕顶部*/
    /*{"flameshot",            NULL,                 NULL,             0,            1,          0,          0,        -1,      0}, // 火焰截图            浮动*/
    /*{"Pcmanfm",              NULL,                 NULL,             0,            1,          0,          1,        -1,      3}, // pcmanfm             浮动、无边框 右上角*/
    /*{"wemeetapp",            NULL,                 NULL,             TAGMASK,      1,          1,          0,        -1,      0}, // !!!腾讯会议在切换tag时有诡异bug导致退出 变成global来规避该问题*/

    /** 部分特殊class的规则 */
    {"float",                NULL,                 NULL,             0,            1,          0,          0,        -1,      0}, // class = float       浮动
    {"global",               NULL,                 NULL,             TAGMASK,      0,          1,          0,        -1,      0}, // class = gloabl      全局
    {"noborder",             NULL,                 NULL,             0,            0,          0,          1,        -1,      0}, // class = noborder    无边框
    {"FGN",                  NULL,                 NULL,             TAGMASK,      1,          1,          1,        -1,      0}, // class = FGN         浮动、全局、无边框
    {"FG",                   NULL,                 NULL,             TAGMASK,      1,          1,          0,        -1,      0}, // class = FG          浮动、全局
    {"FN",                   NULL,                 NULL,             0,            1,          0,          1,        -1,      0}, // class = FN          浮动、无边框
    {"GN",                   NULL,                 NULL,             TAGMASK,      0,          1,          1,        -1,      0}, // CLASS = GN          全局、无边框

    /** 优先度低 越在上面优先度越低 */
    { NULL,                  NULL,                "crx_",            0,            1,          0,          0,        -1,      0}, // 错误载入时 会有crx_ 浮动
    { NULL,                  NULL,                "broken",          0,            1,          0,          0,        -1,      0}, // 错误载入时 会有broken 浮动
};
static const char *overviewtag = "OVERVIEW";
static const Layout overviewlayout = { "󰕬",  overview };

/* 自定义布局 */
static const Layout layouts[] = {
    { "󰯌",  tile },         /* 主次栈 */
    { "󰕰",  magicgrid },    /* 网格   */
};

#define SHCMD(cmd) { .v = (const char*[]){ "/bin/sh", "-c", cmd, NULL } }
#define MODKEY Mod4Mask
#define TAGKEYS(KEY, TAG, cmd) \
    { MODKEY,              KEY, view,       {.ui = 1 << TAG, .v = cmd} }, \
    { MODKEY|ShiftMask,    KEY, tag,        {.ui = 1 << TAG} }, \
    { MODKEY|ControlMask,  KEY, toggleview, {.ui = 1 << TAG} }, \

static Key keys[] = {
    /* modifier            key              function          argument */

    { MODKEY|ShiftMask,    XK_equal,        togglesystray,    {0} },                     /* super shift +      |  切换 托盘栏显示状态 */
    { MODKEY,              XK_j,            focusstack,       {.i = +1} },               /* super j            |  本tag内切换聚焦窗口 */
    { MODKEY,              XK_k,            focusstack,       {.i = -1} },               /* super k            |  本tag内切换聚焦窗口 */
    { MODKEY,              XK_Up,           focusstack,       {.i = -1} },               /* super up           |  本tag内切换聚焦窗口 */
    { MODKEY,              XK_Down,         focusstack,       {.i = +1} },               /* super down         |  本tag内切换聚焦窗口 */

    { MODKEY,              XK_comma,        viewtoleft,       {0} },                     /* super left         |  聚焦到左边的tag */
    { MODKEY,              XK_period,       viewtoright,      {0} },                     /* super right        |  聚焦到右边的tag */
    { MODKEY,              XK_Left,         viewtoleft,       {0} },                     /* super left         |  聚焦到左边的tag */
    { MODKEY,              XK_Right,        viewtoright,      {0} },                     /* super right        |  聚焦到右边的tag */
    { MODKEY|ShiftMask,    XK_Left,         tagtoleft,        {0} },                     /* super shift left   |  将本窗口移动到左边tag */
    { MODKEY|ShiftMask,    XK_Right,        tagtoright,       {0} },                     /* super shift right  |  将本窗口移动到右边tag */

    { MODKEY,              XK_Tab,          toggleoverview,   {0} },                     /* super tab          |  显示所有tag 或 跳转到聚焦窗口的tag */

    // { MODKEY,              XK_minus,        viewtoleft,       {0} },                     /* super left         |  聚焦到左边的tag */
    // { MODKEY,              XK_equal,        viewtoright,      {0} },                     /* super right        |  聚焦到右边的tag */
    { MODKEY,              XK_minus,        setmfact,         {.f = -0.05} },            /* super -            |  缩小主工作区 */
    { MODKEY,              XK_equal,        setmfact,         {.f = +0.05} },            /* super =            |  放大主工作区 */

    { MODKEY,              XK_i,            hidewin,          {0} },                     /* super i            |  隐藏 窗口 */
    { MODKEY|ShiftMask,    XK_i,            restorewin,       {0} },                     /* super shift i      |  取消隐藏 窗口 */

    { MODKEY,              XK_s,            zoom,             {0} },                     /* super s            |  将当前聚焦窗口置为主窗口 */

    { MODKEY,              XK_t,            togglefloating,   {0} },                     /* super t            |  开启/关闭 聚焦目标的float模式 */
    { MODKEY|ShiftMask,    XK_t,            toggleallfloating,{0} },                     /* super shift t      |  开启/关闭 全部目标的float模式 */
    { MODKEY,              XK_f,            fullscreen,       {0} },                     /* super f            |  开启/关闭 全屏 */
    { MODKEY|ShiftMask,    XK_f,            togglebar,        {0} },                     /* super shift f      |  开启/关闭 状态栏 */
    { MODKEY,              XK_g,            toggleglobal,     {0} },                     /* super g            |  开启/关闭 全局 */
    { MODKEY|ShiftMask,    XK_u,            toggleborder,     {0} },                     /* super shift u      |  开启/关闭 边框 */
    { MODKEY,              XK_u,            incnmaster,       {.i = +1} },               /* super u            |  改变主工作区窗口数量 (1 2中切换) */

    { MODKEY,              XK_q,            killclient,       {0} },                     /* super q            |  关闭窗口 */
    { MODKEY|ControlMask,  XK_q,            forcekillclient,  {0} },                     /* super ctrl q       |  强制关闭窗口(处理某些情况下无法销毁的窗口) */
    { MODKEY|ControlMask,  XK_F12,          quit,             {0} },                     /* super ctrl f12     |  退出dwm */

    { MODKEY|ShiftMask,    XK_space,        selectlayout,     {.v = &layouts[1]} },      /* super shift space  |  切换到另一个布局 */
    { MODKEY,              XK_o,            showonlyorall,    {0} },                     /* super o            |  切换 只显示一个窗口 / 全部显示 */

    { MODKEY|ControlMask,  XK_equal,        setgap,           {.i = -6} },               /* super ctrl +       |  窗口增大 */
    { MODKEY|ControlMask,  XK_minus,        setgap,           {.i = +6} },               /* super ctrl -       |  窗口减小 */
    { MODKEY|ControlMask,  XK_space,        setgap,           {.i = 0} },                /* super ctrl space   |  窗口重置 */

    { MODKEY|ControlMask,  XK_Up,           movewin,          {.ui = UP} },              /* super ctrl up      |  移动窗口 */
    { MODKEY|ControlMask,  XK_Down,         movewin,          {.ui = DOWN} },            /* super ctrl down    |  移动窗口 */
    { MODKEY|ControlMask,  XK_Left,         movewin,          {.ui = LEFT} },            /* super ctrl left    |  移动窗口 */
    { MODKEY|ControlMask,  XK_Right,        movewin,          {.ui = RIGHT} },           /* super ctrl right   |  移动窗口 */

    { MODKEY|Mod1Mask,     XK_Up,           resizewin,        {.ui = V_REDUCE} },        /* super alt up       |  调整窗口 */
    { MODKEY|Mod1Mask,     XK_Down,         resizewin,        {.ui = V_EXPAND} },        /* super alt down     |  调整窗口 */
    { MODKEY|Mod1Mask,     XK_Left,         resizewin,        {.ui = H_REDUCE} },        /* super alt left     |  调整窗口 */
    { MODKEY|Mod1Mask,     XK_Right,        resizewin,        {.ui = H_EXPAND} },        /* super alt right    |  调整窗口 */

    { MODKEY,              XK_h,            focusdir,         {.i = LEFT } },            /* super h            | 二维聚焦窗口 */
    { MODKEY,              XK_l,            focusdir,         {.i = RIGHT } },           /* super l            | 二维聚焦窗口 */
    { MODKEY|ShiftMask,    XK_k,            exchange_client,  {.i = UP } },              /* super shift k      | 二维交换窗口 (仅平铺) */
    { MODKEY|ShiftMask,    XK_j,            exchange_client,  {.i = DOWN } },            /* super shift j      | 二维交换窗口 (仅平铺) */
    { MODKEY|ShiftMask,    XK_h,            exchange_client,  {.i = LEFT} },             /* super shift h      | 二维交换窗口 (仅平铺) */
    { MODKEY|ShiftMask,    XK_l,            exchange_client,  {.i = RIGHT } },           /* super shift l      | 二维交换窗口 (仅平铺) */

    /*{ MODKEY,              XK_b,            focusmon,         {.i = +1} },                super b            |  光标移动到另一个显示器 */
    /*{ MODKEY|ShiftMask,    XK_b,            tagmon,           {.i = +1} },                super shift b      |  将聚焦窗口移动到另一个显示器 */

    /* spawn + SHCMD 执行对应命令 */
    { MODKEY,              XK_Return, spawn, SHCMD("alacritty") },                                                      /* super enter      | 打开alacritty终端      */
    { MODKEY,              XK_space,  spawn, SHCMD("alacritty --class float") },                                        /* super space      | 打开浮动 alacritty终端      */
    { MODKEY,              XK_e,      spawn, SHCMD("alacritty -e yazi") },                                              /* super e          | 打开浮动 yazi         */
    { MODKEY,              XK_b,      spawn, SHCMD("vivaldi") },                                                        /* super b          | 打开 vivaldi           */
    { MODKEY,              XK_w,      spawn, SHCMD("rofi -show window") },                                              /* super w          | 打开 rofi window           */
    { Mod1Mask,            XK_Tab,    spawn, SHCMD("rofi -show drun")},                                                 /* alt tab          | 打开rofi run           */ 
    { MODKEY,              XK_p,      spawn, SHCMD("~/Scripts/blurlock.sh") },                                          /* super p          | 锁定屏幕               */
    { MODKEY,              XK_m,      spawn, SHCMD("~/Scripts/rofi.sh") },                                              /* super m          | 自定义脚本              */
    { MODKEY|ShiftMask,    XK_q,      spawn, SHCMD("kill -9 $(xprop | grep _NET_WM_PID | awk '{print $3}')") },         /* super shift q    | 选中某个窗口并强制kill */
    { MODKEY,              XK_n,      togglescratch, SHCMD("alacritty -t scratchpad --class float") },                  /* super n          | 打开便携终端 scratchpad        */

    // { MODKEY|ShiftMask,    XK_Down,   spawn, SHCMD("$DWM/DEF/set_vol.sh down") },                                    /* super shift down | 音量减                 */
    // { MODKEY|ShiftMask,    XK_Up,     spawn, SHCMD("$DWM/DEF/set_vol.sh up") },                                      /* super shift up   | 音量加                 */
    //{ ControlMask|Mod1Mask,XK_a,      spawn, SHCMD("flameshot gui -c -p ~/Pictures/screenshots") },                   /* super shift a    | 截图                   */
    // { MODKEY,              XK_minus,  spawn, SHCMD("st -c FG") },                                                    /* super -          | 打开全局st终端         */
    // { MODKEY|ShiftMask,    XK_p,      spawn, SHCMD("/home/shan/Scripts/shutdown.sh") },                              /* super shift p    | poweroff               */
    // { MODKEY,              XK_d,      spawn, SHCMD("rofi -show run") },                                              /* super d          | rofi: 执行run          */
    // { MODKEY,              XK_p,      spawn, SHCMD("$DWM/DEF/rofi.sh") },                                            /* super p          | rofi: 执行自定义脚本   */
    // { MODKEY,              XK_s,      togglescratch, SHCMD("st -t scratchpad -c float") },                           /* super s          | 打开scratch终端        */


    /* super key : 跳转到对应tag (可附加一条命令 若目标目录无窗口，则执行该命令) */
    /* super shift key : 将聚焦窗口移动到对应tag */
    /* key tag cmd */
    TAGKEYS(XK_1, 0, 0)
    TAGKEYS(XK_2, 1, 0)
    TAGKEYS(XK_3, 2, 0)
    TAGKEYS(XK_4, 3, 0)
    TAGKEYS(XK_5, 4, 0)
    TAGKEYS(XK_0, 8, "linuxqq")
};

static Button buttons[] = {
    /* click               event mask       button            function       argument  */
    /* 点击窗口标题栏操作 */
    { ClkWinTitle,         0,               Button1,          hideotherwins, {0} },                                   // 左键        |  点击标题     |  隐藏其他窗口仅保留该窗口
    { ClkWinTitle,         0,               Button3,          togglewin,     {0} },                                   // 右键        |  点击标题     |  切换窗口显示状态
    /* 点击窗口操作 */
    { ClkClientWin,        MODKEY,          Button1,          movemouse,     {0} },                                   // super+左键  |  拖拽窗口     |  拖拽窗口
    { ClkClientWin,        MODKEY,          Button3,          resizemouse,   {0} },                                   // super+右键  |  拖拽窗口     |  改变窗口大小
    /* 点击tag操作 */
    { ClkTagBar,           0,               Button1,          view,          {0} },                                   // 左键        |  点击tag      |  切换tag
    { ClkTagBar,           0,               Button3,          toggleview,    {0} },                                   // 右键        |  点击tag      |  切换是否显示tag
    { ClkTagBar,           MODKEY,          Button1,          tag,           {0} },                                   // super+左键  |  点击tag      |  将窗口移动到对应tag
    { ClkTagBar,           0,               Button4,          viewtoleft,    {0} },                                   // 鼠标滚轮上  |  tag          |  向前切换tag
    { ClkTagBar,           0,               Button5,          viewtoright,   {0} },                                   // 鼠标滚轮下  |  tag          |  向后切换tag
    /* 点击状态栏操作 */
    { ClkStatusText,       0,               Button1,          clickstatusbar,{0} },                                   // 左键        |  点击状态栏   |  根据状态栏的信号执行 ~/scripts/dwmstatusbar.sh $signal L
    { ClkStatusText,       0,               Button2,          clickstatusbar,{0} },                                   // 中键        |  点击状态栏   |  根据状态栏的信号执行 ~/scripts/dwmstatusbar.sh $signal M
    { ClkStatusText,       0,               Button3,          clickstatusbar,{0} },                                   // 右键        |  点击状态栏   |  根据状态栏的信号执行 ~/scripts/dwmstatusbar.sh $signal R
    { ClkStatusText,       0,               Button4,          clickstatusbar,{0} },                                   // 鼠标滚轮上  |  状态栏       |  根据状态栏的信号执行 ~/scripts/dwmstatusbar.sh $signal U
    { ClkStatusText,       0,               Button5,          clickstatusbar,{0} },                                   // 鼠标滚轮下  |  状态栏       |  根据状态栏的信号执行 ~/scripts/dwmstatusbar.sh $signal D

    /* 点击bar空白处 */
    // { ClkBarEmpty,         0,               Button1,          spawn, SHCMD("~/scripts/call_rofi.sh window") },        // 左键        |  bar空白处    |  rofi 执行 window
    // { ClkBarEmpty,         0,               Button3,          spawn, SHCMD("~/scripts/call_rofi.sh drun") },          // 右键        |  bar空白处    |  rofi 执行 drun
};