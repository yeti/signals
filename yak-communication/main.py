import click
from parser.api import Schema
from generators.ios.ios_generator import iOSGenerator

generators = {
    'ios': iOSGenerator
}

@click.command()
@click.option('--schema',
              prompt='path to api schema file',
              help='The server\'s API schema file.',
              type=click.Path(exists=True))
@click.option('--generator',
              prompt='name of generator to use',
              help='The name of the generator you\'d like to use.',
              type=click.Choice(generators.keys()))
# TODO: These are iOS specific settings and we'll need to figure out a way to handle generator specific arguments
# when we add more generators in the future.
@click.option('data_models', '--datamodels',
              prompt='path to iOS data models',
              help='The location where you\'d like your iOS data model files stored.',
              type=click.Path())
@click.option('core_data', '--coredata',
              help='The location of your core data configuration xcdatamodel file.',
              type=click.Path(exists=True))
def main_loop(schema, generator, data_models, core_data):
    schema = Schema(schema)
    generator = generators[generator](schema, data_models, core_data)
    generator.process()

    print("Finished generator your files!")


if __name__ == '__main__':
    main_loop()
