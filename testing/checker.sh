# We need a way to test the output of environment variables, within the
# command that is called. I can't seem to get stdout redirection within
# a subprocess, so we create ourselves a method for retrieving output
# from within this process.
env | grep 'SECRET_' > "$1"