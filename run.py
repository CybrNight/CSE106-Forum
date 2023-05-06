
import sys
import getopt

options = {}


def parse_args(argv):
    '''
    Parses command line arguments for running Flask app

    Paramters:
    argv (list): List of paramters to be parsed
    '''
    try:
        # Get opts and args from input
        opts, args = getopt.getopt(argv, "rd")

        # Iterate over each opt and arg
        for opt, arg in opts:

            # Set switches based on opt value
            if opt == '-r':
                options['rebuild'] = True
            if opt == '-d':
                options['debug'] = True

    except getopt.GetoptError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    from forum import run_app
    parse_args(sys.argv[1:])

    debug = options.get('debug') == True
    rebuild = options.get('rebuild') == True

    run_app(debug=debug, rebuild=rebuild)
