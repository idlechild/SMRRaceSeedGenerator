:: SMR_DISCORD_ROLES_CHANNEL and SMR_DISCORD_SEEDS_CHANNEL are optional can can be removed
@ECHO OFF
docker run ^
    -e SMR_DISCORD_TOKEN=%SMR_DISCORD_TOKEN% ^
    -e SMR_DISCORD_SANDBOX_CHANNEL=%SMR_DISCORD_SANDBOX_CHANNEL% ^
    -e SMR_DISCORD_ROLES_CHANNEL=%SMR_DISCORD_ROLES_CHANNEL% ^
    -e SMR_DISCORD_SEEDS_CHANNEL=%SMR_DISCORD_SEEDS_CHANNEL% ^
    -d smr

