import api
import cProfile

def your_function_to_profile():
    api.gamedata_api("/ProgramData", "POST", 1)

# Create a cProfile object
profiler = cProfile.Profile()

# Start profiling
profiler.enable()

# Call the function you want to profile
your_function_to_profile()

# Stop profiling
profiler.disable()

# Print the profiling results
profiler.print_stats()