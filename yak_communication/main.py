from __future__ import absolute_import
import click

from yak_communication.parser.schema import Schema
from yak_communication.generators.ios.ios_generator import iOSGenerator
from yak_communication.settings import save_settings
from yak_communication.settings import load_settings
from yak_communication.logging import SignalsError, progress


generators = {
    'ios': iOSGenerator
}


# Create a separate function so that we can unit test.
# Issues unit testing `main` due to click decorators.
def run_main(schema, generator_name, data_models, core_data, project_name, save):
    schema = Schema(schema)
    generator = generators[generator_name](schema, data_models, core_data, project_name)
    try:
        generator.process()
        if save:
            save_settings([data_models, core_data], schema, generator_name, data_models, core_data, project_name)
    except SignalsError as e:
        print(str(e))
    else:
        progress('Finished generating your files!')


def project_specified(ctx, param, value):
    if not value or (not ctx is None and ctx.resilient_parsing):
        return

    try:
        setting_dict = load_settings(value)
    except SignalsError as e:
        print(str(e))
    else:
        run_main(setting_dict["schema"],
                 setting_dict["generator"],
                 setting_dict["data_models"],
                 setting_dict["core_data"],
                 setting_dict["project_name"],
                 False)

    if not ctx is None:
        ctx.exit()

@click.command()
@click.option('settings_path', '--settingspath',
              help='The project path where Signals should look for a .signalsconfig file.  If specified, the contents'
                   ' of the file are used instead of any other specified options',
              type=click.Path(),
              callback=project_specified,
              is_eager=True)
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
@click.option('--save', is_flag=True)
# TODO: These are iOS specific settings and we'll need to figure out a way to handle generator specific arguments
# when we add more generators in the future.
def main(settings_path, schema, generator, data_models, core_data, project_name, save):
    run_main(schema, generator, data_models, core_data, project_name, save)
