import click
from signals.parser.schema import Schema
from signals.generators.ios.ios_generator import iOSGenerator
from signals.logging import SignalsError, progress

generators = {
    'ios': iOSGenerator
}

# Create a separate function so that we can unit test.
# Issues unit testing `main` due to click decorators.
def run_main(schema, generator, data_models, core_data, project_name, api_url):
    schema = Schema(schema)
    generator = generators[generator](schema, data_models, core_data, project_name, api_url)
    try:
        generator.process()
    except SignalsError as e:
        print(str(e))
    else:
        progress('Finished generating your files!')


@click.command()
@click.option('--schema',
              prompt='path to api schema file',
              help='The server\'s API schema file.',
              type=click.Path(exists=True))
@click.option('--generator',
              prompt='name of generator to use',
              help='The name of the generator you\'d like to use.',
              type=click.Choice(generators.keys()))
@click.option('data_models', '--datamodels',
              prompt='path to iOS data models',
              help='The location where you\'d like your iOS data model files stored.',
              type=click.Path())
@click.option('core_data', '--coredata',
              help='The location of your core data configuration xcdatamodel file.',
              type=click.Path(exists=True))
@click.option('project_name', '--projectname',
              prompt="name of your iOS project and main target",
              help='The name of your iOS project and main target.',
              type=click.STRING)
@click.option('api_url', '--apiurl',
              prompt='the url of your api',
              help='The fully qualified url of your API for making calls',
              type=click.STRING)
# TODO: These are iOS specific settings and we'll need to figure out a way to handle generator specific arguments
# when we add more generators in the future.
def main(schema, generator, data_models, core_data, project_name, api_url):
    run_main(schema, generator, data_models, core_data, project_name, api_url)
