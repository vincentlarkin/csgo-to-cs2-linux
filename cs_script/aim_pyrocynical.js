import { Instance, Console } from "cs_script/point_script";

// aim_pyrocynical's original CS:GO rules, applied only in the Custom game mode (game_type 3 /
// game_mode 0 in gamemodes.txt): endless rounds, no warmup or time limit, $16000, unlimited
// buy time, all-talk, and a bot to 1v1. Casual, Competitive and Deathmatch keep their stock
// rules, and their configs reset all of these except all-talk and mp_limitteams on the next map.
// The original also flicked sv_cheats on and off at spawn, which changed nothing; left out.
const GAME_TYPE_CUSTOM = 3;
const GAME_MODE_CUSTOM = 0;

const RULES = {
    mp_limitteams: 999,
    mp_roundtime: 9999,
    mp_roundtime_hostage: 9999,
    mp_startmoney: 16000,
    mp_buytime: 9999,
    mp_maxrounds: 9999,
    mp_timelimit: 0,
    mp_freezetime: 0,
    sv_alltalk: 1,
    sv_deadtalk: 1,
    bot_quota: 2,
    mp_weapons_allow_map_placed: 1,
};

Instance.OnActivate(() => {
    if (Instance.GetGameType() !== GAME_TYPE_CUSTOM || Instance.GetGameMode() !== GAME_MODE_CUSTOM) return;
    for (const [name, value] of Object.entries(RULES)) Console.SetConvar(name, value);
    Console.ServerCommand("mp_warmup_end");
    Console.ServerCommand("mp_unpause_match");
});
