import { Instance, CSGearSlot } from "cs_script/point_script";

// awp_neon's original CS:GO rules (knife + AWP + armor, no buying), applied only in the
// Custom game mode (game_type 3 / game_mode 0 in gamemodes.txt). Casual, Competitive,
// Deathmatch etc. keep their stock rules. No convars are touched, so nothing leaks into
// later maps.
const GAME_TYPE_CUSTOM = 3;
const GAME_MODE_CUSTOM = 0;
// Everything except the knife, so players keep their own loadout knife.
const STRIPPED_SLOTS = [CSGearSlot.RIFLE, CSGearSlot.PISTOL, CSGearSlot.GRENADES, CSGearSlot.C4];

function isCustomMode() {
    return Instance.GetGameType() === GAME_TYPE_CUSTOM && Instance.GetGameMode() === GAME_MODE_CUSTOM;
}

// The map's buy zones serve the other modes; in Custom they are switched off. Map entities
// are restored on round restart, so this runs every round.
function disableBuyZones() {
    if (!isCustomMode()) return;
    for (const name of ["buyzone_t", "buyzone_ct"]) Instance.EntFireAtName({ name, input: "Disable" });
}
Instance.OnActivate(disableBuyZones);
Instance.OnRoundStart(disableBuyZones);

// Fires when a player respawns, changes team, or is put back at spawn by a round restart.
Instance.OnPlayerReset(({ player }) => {
    if (!isCustomMode() || !player?.IsValid()) return;
    for (const slot of STRIPPED_SLOTS) {
        // A slot can hold several items (grenades); the cap guards against a weapon that
        // lingers until the end of the tick.
        for (let i = 0; i < 8; i++) {
            const weapon = player.FindWeaponBySlot(slot);
            if (!weapon) break;
            player.DestroyWeapon(weapon);
        }
    }
    if (!player.FindWeaponBySlot(CSGearSlot.KNIFE)) player.GiveNamedItem("weapon_knife");
    player.GiveNamedItem("weapon_awp", true);
    player.SetArmor(100);
});
