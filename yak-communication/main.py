import click


@click.command()
@click.option('--schema', prompt='Path to api schema file', help='The server\'s API schema file.')
def main_loop(schema):
    print "schema: " + schema



if __name__ == '__main__':
    main_loop()