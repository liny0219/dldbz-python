from tool_build_base import main

type = 'patch'
# type = 'minor'
# type = 'major'

version = '2.4.0'

if __name__ == '__main__':
    main(type, version)
