import os
import json
types = """[
    {
        "id": "7d2d",
        "name": "7 Days to Die (2013)"
    },
    {
        "id": "ageofchivalry",
        "name": "Age of Chivalry (2007)"
    },
    {
        "id": "aoe2",
        "name": "Age of Empires 2 (1999)"
    },
    {
        "id": "alienarena",
        "name": "Alien Arena (2004)"
    },
    {
        "id": "alienswarm",
        "name": "Alien Swarm (2010)"
    },
    {
        "id": "avp2",
        "name": "Aliens versus Predator 2 (2001)"
    },
    {
        "id": "avp2010",
        "name": "Aliens vs. Predator (2010)"
    },
    {
        "id": "americasarmy",
        "name": "America's Army (2002)"
    },
    {
        "id": "americasarmy2",
        "name": "America's Army 2 (2003)"
    },
    {
        "id": "americasarmy3",
        "name": "America's Army 3 (2009)"
    },
    {
        "id": "americasarmypg",
        "name": "America's Army: Proving Grounds (2015)"
    },
    {
        "id": "arcasimracing",
        "name": "Arca Sim Racing (2008)"
    },
    {
        "id": "arkse",
        "name": "Ark: Survival Evolved (2017)"
    },
    {
        "id": "arma2",
        "name": "ARMA 2 (2009)"
    },
    {
        "id": "arma2oa",
        "name": "ARMA 2: Operation Arrowhead (2010)"
    },
    {
        "id": "arma3",
        "name": "ARMA 3 (2013)"
    },
    {
        "id": "arma",
        "name": "ARMA: Armed Assault (2007)"
    },
    {
        "id": "armacwa",
        "name": "ARMA: Cold War Assault (2011)"
    },
    {
        "id": "armar",
        "name": "ARMA: Resistance (2011)"
    },
    {
        "id": "armagetron",
        "name": "Armagetron Advanced (2001)"
    },
    {
        "id": "assettocorsa",
        "name": "Assetto Corsa (2014)"
    },
    {
        "id": "atlas",
        "name": "Atlas (2018)"
    },
    {
        "id": "baldursgate",
        "name": "Baldur's Gate (1998)"
    },
    {
        "id": "bat1944",
        "name": "Battalion 1944 (2018)"
    },
    {
        "id": "bf1942",
        "name": "Battlefield 1942 (2002)"
    },
    {
        "id": "bf2",
        "name": "Battlefield 2 (2005)"
    },
    {
        "id": "bf2142",
        "name": "Battlefield 2142 (2006)"
    },
    {
        "id": "bf3",
        "name": "Battlefield 3 (2011)"
    },
    {
        "id": "bf4",
        "name": "Battlefield 4 (2013)"
    },
    {
        "id": "bfh",
        "name": "Battlefield Hardline (2015)"
    },
    {
        "id": "bfv",
        "name": "Battlefield Vietnam (2004)"
    },
    {
        "id": "bfbc2",
        "name": "Battlefield: Bad Company 2 (2010)"
    },
    {
        "id": "breach",
        "name": "Breach (2011)"
    },
    {
        "id": "breed",
        "name": "Breed (2004)"
    },
    {
        "id": "brink",
        "name": "Brink (2011)"
    },
    {
        "id": "buildandshoot",
        "name": "Build and Shoot / Ace of Spades Classic (2012)"
    },
    {
        "id": "cod",
        "name": "Call of Duty (2003)"
    },
    {
        "id": "cod2",
        "name": "Call of Duty 2 (2005)"
    },
    {
        "id": "cod3",
        "name": "Call of Duty 3 (2006)"
    },
    {
        "id": "cod4",
        "name": "Call of Duty 4: Modern Warfare (2007)"
    },
    {
        "id": "codmw2",
        "name": "Call of Duty: Modern Warfare 2 (2009)"
    },
    {
        "id": "codmw3",
        "name": "Call of Duty: Modern Warfare 3 (2011)"
    },
    {
        "id": "coduo",
        "name": "Call of Duty: United Offensive (2004)"
    },
    {
        "id": "codwaw",
        "name": "Call of Duty: World at War (2008)"
    },
    {
        "id": "callofjuarez",
        "name": "Call of Juarez (2006)"
    },
    {
        "id": "chaser",
        "name": "Chaser (2003)"
    },
    {
        "id": "chrome",
        "name": "Chrome (2003)"
    },
    {
        "id": "codenameeagle",
        "name": "Codename Eagle (2000)"
    },
    {
        "id": "cacrenegade",
        "name": "Command and Conquer: Renegade (2002)"
    },
    {
        "id": "commandos3",
        "name": "Commandos 3: Destination Berlin (2003)"
    },
    {
        "id": "conanexiles",
        "name": "Conan Exiles (2018)"
    },
    {
        "id": "contagion",
        "name": "Contagion (2011)"
    },
    {
        "id": "contactjack",
        "name": "Contract J.A.C.K. (2003)"
    },
    {
        "id": "cs15",
        "name": "Counter-Strike 1.5 (2002)"
    },
    {
        "id": "cs16",
        "name": "Counter-Strike 1.6 (2003)"
    },
    {
        "id": "cs2d",
        "name": "Counter-Strike: 2D (2004)"
    },
    {
        "id": "cscz",
        "name": "Counter-Strike: Condition Zero (2004)"
    },
    {
        "id": "csgo",
        "name": "Counter-Strike: Global Offensive (2012)"
    },
    {
        "id": "css",
        "name": "Counter-Strike: Source (2004)"
    },
    {
        "id": "crossracing",
        "name": "Cross Racing Championship Extreme 2005 (2005)"
    },
    {
        "id": "crysis",
        "name": "Crysis (2007)"
    },
    {
        "id": "crysis2",
        "name": "Crysis 2 (2011)"
    },
    {
        "id": "crysiswars",
        "name": "Crysis Wars (2008)"
    },
    {
        "id": "daikatana",
        "name": "Daikatana (2000)"
    },
    {
        "id": "dnl",
        "name": "Dark and Light (2017)"
    },
    {
        "id": "dmomam",
        "name": "Dark Messiah of Might and Magic (2006)"
    },
    {
        "id": "darkesthour",
        "name": "Darkest Hour: Europe '44-'45 (2008)"
    },
    {
        "id": "dod",
        "name": "Day of Defeat (2003)"
    },
    {
        "id": "dods",
        "name": "Day of Defeat: Source (2005)"
    },
    {
        "id": "doi",
        "name": "Day of Infamy (2017)"
    },
    {
        "id": "daysofwar",
        "name": "Days of War (2017)"
    },
    {
        "id": "dayz",
        "name": "DayZ (2018)"
    },
    {
        "id": "dayzmod",
        "name": "DayZ Mod (2013)"
    },
    {
        "id": "deadlydozenpt",
        "name": "Deadly Dozen: Pacific Theater (2002)"
    },
    {
        "id": "dh2005",
        "name": "Deer Hunter 2005 (2004)"
    },
    {
        "id": "descent3",
        "name": "Descent 3 (1999)"
    },
    {
        "id": "deusex",
        "name": "Deus Ex (2000)"
    },
    {
        "id": "devastation",
        "name": "Devastation (2003)"
    },
    {
        "id": "dinodday",
        "name": "Dino D-Day (2011)"
    },
    {
        "id": "dirttrackracing2",
        "name": "Dirt Track Racing 2 (2002)"
    },
    {
        "id": "doom3",
        "name": "Doom 3 (2004)"
    },
    {
        "id": "dota2",
        "name": "Dota 2 (2013)"
    },
    {
        "id": "drakan",
        "name": "Drakan: Order of the Flame (1999)"
    },
    {
        "id": "empyrion",
        "name": "Empyrion - Galactic Survival (2015)"
    },
    {
        "id": "etqw",
        "name": "Enemy Territory: Quake Wars (2007)"
    },
    {
        "id": "fear",
        "name": "F.E.A.R. (2005)"
    },
    {
        "id": "f1c9902",
        "name": "F1 Challenge '99-'02 (2002)"
    },
    {
        "id": "farcry",
        "name": "Far Cry (2004)"
    },
    {
        "id": "farcry2",
        "name": "Far Cry 2 (2008)"
    },
    {
        "id": "f12002",
        "name": "Formula One 2002 (2002)"
    },
    {
        "id": "fortressforever",
        "name": "Fortress Forever (2007)"
    },
    {
        "id": "ffow",
        "name": "Frontlines: Fuel of War (2008)"
    },
    {
        "id": "garrysmod",
        "name": "Garry's Mod (2004)"
    },
    {
        "id": "geneshiftmutantfactions",
        "name": "Geneshift (2017)"
    },
    {
        "id": "giantscitizenkabuto",
        "name": "Giants: Citizen Kabuto (2000)"
    },
    {
        "id": "globaloperations",
        "name": "Global Operations (2002)"
    },
    {
        "id": "ges",
        "name": "GoldenEye: Source (2010)"
    },
    {
        "id": "gore",
        "name": "Gore: Ultimate Soldier (2002)"
    },
    {
        "id": "fivem",
        "name": "Grand Theft Auto V - FiveM (2013)"
    },
    {
        "id": "mtasa",
        "name": "Grand Theft Auto: San Andreas - Multi Theft Auto (2004)"
    },
    {
        "id": "mtavc",
        "name": "Grand Theft Auto: Vice City - Multi Theft Auto (2002)"
    },
    {
        "id": "gunmanchronicles",
        "name": "Gunman Chronicles (2000)"
    },
    {
        "id": "hl2dm",
        "name": "Half-Life 2: Deathmatch (2004)"
    },
    {
        "id": "hldm",
        "name": "Half-Life Deathmatch (1998)"
    },
    {
        "id": "hldms",
        "name": "Half-Life Deathmatch: Source (2005)"
    },
    {
        "id": "halo",
        "name": "Halo (2003)"
    },
    {
        "id": "halo2",
        "name": "Halo 2 (2007)"
    },
    {
        "id": "hll",
        "name": "Hell Let Loose"
    },
    {
        "id": "heretic2",
        "name": "Heretic II (1998)"
    },
    {
        "id": "hexen2",
        "name": "Hexen II (1997)"
    },
    {
        "id": "had2",
        "name": "Hidden & Dangerous 2 (2003)"
    },
    {
        "id": "homefront",
        "name": "Homefront (2011)"
    },
    {
        "id": "homeworld2",
        "name": "Homeworld 2 (2003)"
    },
    {
        "id": "hurtworld",
        "name": "Hurtworld (2015)"
    },
    {
        "id": "igi2",
        "name": "I.G.I.-2: Covert Strike (2003)"
    },
    {
        "id": "il2",
        "name": "IL-2 Sturmovik (2001)"
    },
    {
        "id": "insurgency",
        "name": "Insurgency (2014)"
    },
    {
        "id": "insurgencysandstorm",
        "name": "Insurgency: Sandstorm (2018)"
    },
    {
        "id": "ironstorm",
        "name": "Iron Storm (2002)"
    },
    {
        "id": "jamesbondnightfire",
        "name": "James Bond 007: Nightfire (2002)"
    },
    {
        "id": "jc2mp",
        "name": "Just Cause 2 - Multiplayer (2010)"
    },
    {
        "id": "jc3mp",
        "name": "Just Cause 3 - Multiplayer (2017)"
    },
    {
        "id": "kspdmp",
        "name": "Kerbal Space Program - DMP Multiplayer (2015)"
    },
    {
        "id": "killingfloor",
        "name": "Killing Floor (2009)"
    },
    {
        "id": "killingfloor2",
        "name": "Killing Floor 2 (2016)"
    },
    {
        "id": "kingpin",
        "name": "Kingpin: Life of Crime (1999)"
    },
    {
        "id": "kisspc",
        "name": "Kiss: Psycho Circus: The Nightmare Child (2000)"
    },
    {
        "id": "kzmod",
        "name": "Kreedz Climbing (2017)"
    },
    {
        "id": "left4dead",
        "name": "Left 4 Dead (2008)"
    },
    {
        "id": "left4dead2",
        "name": "Left 4 Dead 2 (2009)"
    },
    {
        "id": "m2mp",
        "name": "Mafia II - Multiplayer (2010)"
    },
    {
        "id": "m2o",
        "name": "Mafia II - Online (2010)"
    },
    {
        "id": "moh2010",
        "name": "Medal of Honor (2010)"
    },
    {
        "id": "mohab",
        "name": "Medal of Honor: Airborne (2007)"
    },
    {
        "id": "mohaa",
        "name": "Medal of Honor: Allied Assault (2002)"
    },
    {
        "id": "mohbt",
        "name": "Medal of Honor: Allied Assault Breakthrough (2003)"
    },
    {
        "id": "mohsh",
        "name": "Medal of Honor: Allied Assault Spearhead (2002)"
    },
    {
        "id": "mohpa",
        "name": "Medal of Honor: Pacific Assault (2004)"
    },
    {
        "id": "mohwf",
        "name": "Medal of Honor: Warfighter (2012)"
    },
    {
        "id": "medievalengineers",
        "name": "Medieval Engineers (2015)"
    },
    {
        "id": "minecraftminecraftping",
        "name": "Minecraft (2009)"
    },
    {
        "id": "minecraftpeminecraftbe",
        "name": "Minecraft: Bedrock Edition (2011)"
    },
    {
        "id": "mnc",
        "name": "Monday Night Combat (2011)"
    },
    {
        "id": "mordhau",
        "name": "Mordhau (2019)"
    },
    {
        "id": "mumble",
        "name": "Mumble - GTmurmur Plugin (2005)"
    },
    {
        "id": "mumbleping",
        "name": "Mumble - Lightweight (2005)"
    },
    {
        "id": "nascarthunder2004",
        "name": "NASCAR Thunder 2004 (2003)"
    },
    {
        "id": "ns",
        "name": "Natural Selection (2002)"
    },
    {
        "id": "ns2",
        "name": "Natural Selection 2 (2012)"
    },
    {
        "id": "nfshp2",
        "name": "Need for Speed: Hot Pursuit 2 (2002)"
    },
    {
        "id": "nab",
        "name": "Nerf Arena Blast (1999)"
    },
    {
        "id": "netpanzer",
        "name": "netPanzer (2002)"
    },
    {
        "id": "nwn",
        "name": "Neverwinter Nights (2002)"
    },
    {
        "id": "nwn2",
        "name": "Neverwinter Nights 2 (2006)"
    },
    {
        "id": "nexuiz",
        "name": "Nexuiz (2005)"
    },
    {
        "id": "nitrofamily",
        "name": "Nitro Family (2004)"
    },
    {
        "id": "nmrih",
        "name": "No More Room in Hell (2011)"
    },
    {
        "id": "nolf2",
        "name": "No One Lives Forever 2: A Spy in H.A.R.M.'s Way (2002)"
    },
    {
        "id": "nucleardawn",
        "name": "Nuclear Dawn (2011)"
    },
    {
        "id": "openarena",
        "name": "OpenArena (2005)"
    },
    {
        "id": "openttd",
        "name": "OpenTTD (2004)"
    },
    {
        "id": "operationflashpointflashpoint",
        "name": "Operation Flashpoint: Cold War Crisis (2001)"
    },
    {
        "id": "flashpointresistance",
        "name": "Operation Flashpoint: Resistance (2002)"
    },
    {
        "id": "painkiller",
        "name": "Painkiller"
    },
    {
        "id": "pixark",
        "name": "PixARK (2018)"
    },
    {
        "id": "postal2",
        "name": "Postal 2"
    },
    {
        "id": "prey",
        "name": "Prey"
    },
    {
        "id": "primalcarnage",
        "name": "Primal Carnage: Extinction"
    },
    {
        "id": "prbf2",
        "name": "Project Reality: Battlefield 2 (2005)"
    },
    {
        "id": "quake1",
        "name": "Quake 1: QuakeWorld (1996)"
    },
    {
        "id": "quake2",
        "name": "Quake 2 (1997)"
    },
    {
        "id": "quake3",
        "name": "Quake 3: Arena (1999)"
    },
    {
        "id": "quake4",
        "name": "Quake 4 (2005)"
    },
    {
        "id": "quakelive",
        "name": "Quake Live (2010)"
    },
    {
        "id": "ragdollkungfu",
        "name": "Rag Doll Kung Fu"
    },
    {
        "id": "r6",
        "name": "Rainbow Six"
    },
    {
        "id": "r6roguespear",
        "name": "Rainbow Six 2: Rogue Spear"
    },
    {
        "id": "r6ravenshield",
        "name": "Rainbow Six 3: Raven Shield"
    },
    {
        "id": "rallisportchallenge",
        "name": "RalliSport Challenge"
    },
    {
        "id": "rallymasters",
        "name": "Rally Masters"
    },
    {
        "id": "redorchestra",
        "name": "Red Orchestra"
    },
    {
        "id": "redorchestra2",
        "name": "Red Orchestra 2"
    },
    {
        "id": "redorchestraost",
        "name": "Red Orchestra: Ostfront 41-45"
    },
    {
        "id": "redline",
        "name": "Redline"
    },
    {
        "id": "rtcw",
        "name": "Return to Castle Wolfenstein"
    },
    {
        "id": "rfactor",
        "name": "rFactor"
    },
    {
        "id": "ricochet",
        "name": "Ricochet"
    },
    {
        "id": "riseofnations",
        "name": "Rise of Nations"
    },
    {
        "id": "rs2",
        "name": "Rising Storm 2: Vietnam"
    },
    {
        "id": "rune",
        "name": "Rune"
    },
    {
        "id": "rust",
        "name": "Rust"
    },
    {
        "id": "stalker",
        "name": "S.T.A.L.K.E.R."
    },
    {
        "id": "samp",
        "name": "San Andreas Multiplayer"
    },
    {
        "id": "savage2",
        "name": "Savage 2: A Tortured Soul (2008)"
    },
    {
        "id": "ss",
        "name": "Serious Sam"
    },
    {
        "id": "ss2",
        "name": "Serious Sam 2"
    },
    {
        "id": "shatteredhorizon",
        "name": "Shattered Horizon"
    },
    {
        "id": "shogo",
        "name": "Shogo"
    },
    {
        "id": "shootmania",
        "name": "Shootmania"
    },
    {
        "id": "sin",
        "name": "SiN"
    },
    {
        "id": "sinep",
        "name": "SiN Episodes"
    },
    {
        "id": "soldat",
        "name": "Soldat"
    },
    {
        "id": "sof",
        "name": "Soldier of Fortune"
    },
    {
        "id": "sof2",
        "name": "Soldier of Fortune 2"
    },
    {
        "id": "spaceengineers",
        "name": "Space Engineers"
    },
    {
        "id": "squad",
        "name": "Squad"
    },
    {
        "id": "stbc",
        "name": "Star Trek: Bridge Commander"
    },
    {
        "id": "stvef",
        "name": "Star Trek: Voyager - Elite Force"
    },
    {
        "id": "stvef2",
        "name": "Star Trek: Voyager - Elite Force 2"
    },
    {
        "id": "swjk2",
        "name": "Star Wars Jedi Knight II: Jedi Outcast (2002)"
    },
    {
        "id": "swjk",
        "name": "Star Wars Jedi Knight: Jedi Academy (2003)"
    },
    {
        "id": "swbf",
        "name": "Star Wars: Battlefront"
    },
    {
        "id": "swbf2",
        "name": "Star Wars: Battlefront 2"
    },
    {
        "id": "swrc",
        "name": "Star Wars: Republic Commando"
    },
    {
        "id": "starbound",
        "name": "Starbound"
    },
    {
        "id": "starmade",
        "name": "StarMade"
    },
    {
        "id": "starsiege",
        "name": "Starsiege (2009)"
    },
    {
        "id": "suicidesurvival",
        "name": "Suicide Survival"
    },
    {
        "id": "svencoop",
        "name": "Sven Coop"
    },
    {
        "id": "swat4",
        "name": "SWAT 4"
    },
    {
        "id": "synergy",
        "name": "Synergy"
    },
    {
        "id": "tacticalops",
        "name": "Tactical Ops"
    },
    {
        "id": "takeonhelicopters",
        "name": "Take On Helicopters (2011)"
    },
    {
        "id": "teamfactor",
        "name": "Team Factor"
    },
    {
        "id": "tf2",
        "name": "Team Fortress 2"
    },
    {
        "id": "tfc",
        "name": "Team Fortress Classic"
    },
    {
        "id": "teamspeak2",
        "name": "Teamspeak 2"
    },
    {
        "id": "teamspeak3",
        "name": "Teamspeak 3"
    },
    {
        "id": "terminus",
        "name": "Terminus"
    },
    {
        "id": "terrariatshock",
        "name": "Terraria - TShock (2011)"
    },
    {
        "id": "forrest",
        "name": "The Forrest (2014)"
    },
    {
        "id": "hidden",
        "name": "The Hidden (2005)"
    },
    {
        "id": "nolf",
        "name": "The Operative: No One Lives Forever (2000)"
    },
    {
        "id": "ship",
        "name": "The Ship"
    },
    {
        "id": "graw",
        "name": "Tom Clancy's Ghost Recon Advanced Warfighter (2006)"
    },
    {
        "id": "graw2",
        "name": "Tom Clancy's Ghost Recon Advanced Warfighter 2 (2007)"
    },
    {
        "id": "thps3",
        "name": "Tony Hawk's Pro Skater 3"
    },
    {
        "id": "thps4",
        "name": "Tony Hawk's Pro Skater 4"
    },
    {
        "id": "thu2",
        "name": "Tony Hawk's Underground 2"
    },
    {
        "id": "towerunite",
        "name": "Tower Unite"
    },
    {
        "id": "trackmania2",
        "name": "Trackmania 2"
    },
    {
        "id": "trackmaniaforever",
        "name": "Trackmania Forever"
    },
    {
        "id": "tremulous",
        "name": "Tremulous"
    },
    {
        "id": "tribes1",
        "name": "Tribes 1: Starsiege"
    },
    {
        "id": "tribesvengeance",
        "name": "Tribes: Vengeance"
    },
    {
        "id": "tron20",
        "name": "Tron 2.0"
    },
    {
        "id": "turok2",
        "name": "Turok 2"
    },
    {
        "id": "universalcombat",
        "name": "Universal Combat"
    },
    {
        "id": "unreal",
        "name": "Unreal"
    },
    {
        "id": "ut",
        "name": "Unreal Tournament"
    },
    {
        "id": "ut2003",
        "name": "Unreal Tournament 2003"
    },
    {
        "id": "ut2004",
        "name": "Unreal Tournament 2004"
    },
    {
        "id": "ut3",
        "name": "Unreal Tournament 3"
    },
    {
        "id": "unturned",
        "name": "unturned"
    },
    {
        "id": "urbanterror",
        "name": "Urban Terror"
    },
    {
        "id": "v8supercar",
        "name": "V8 Supercar Challenge"
    },
    {
        "id": "ventrilo",
        "name": "Ventrilo"
    },
    {
        "id": "vcmp",
        "name": "Vice City Multiplayer"
    },
    {
        "id": "vietcong",
        "name": "Vietcong"
    },
    {
        "id": "vietcong2",
        "name": "Vietcong 2"
    },
    {
        "id": "warsow",
        "name": "Warsow"
    },
    {
        "id": "wheeloftime",
        "name": "Wheel of Time"
    },
    {
        "id": "wolfenstein2009",
        "name": "Wolfenstein 2009"
    },
    {
        "id": "wolfensteinet",
        "name": "Wolfenstein: Enemy Territory"
    },
    {
        "id": "xpandrally",
        "name": "Xpand Rally"
    },
    {
        "id": "zombiemaster",
        "name": "Zombie Master"
    },
    {
        "id": "zps",
        "name": "Zombie Panic: Source"
    }
]"""
types = json.loads(types)
result = os.popen("gamedig --type fivem 5.9.200.179:30555").read()
result = json.loads(result)
print(f"Got server - {result['name']}, currently there are {len(result['players'])} players online.")