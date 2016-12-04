from gym.envs.registration import register

register(
    id='catch-v0',
    entry_point='gym_catch.envs:CatchEnv',
    timestep_limit=1000,
)