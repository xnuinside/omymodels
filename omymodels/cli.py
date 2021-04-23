import argparse
import os
import sys
from omymodels import create_models
import pprint


def version(**kwargs):
    return "0.2.0"


def cli():
    omm_cli = argparse.ArgumentParser(
        description="O! My Models. Create GinoORM models from SQL DDL"
    )

    omm_cli.add_argument(
        "-m",
        "--models_type",
        type=str,
        default="gino",
        help="The type of model you want to generate, pass as argument one of the supported: [gino, pydantic]",
    )

    omm_cli.add_argument(
        "ddl_file_path",
        type=str,
        help="The path to ddl file that use to generate models",
    )

    omm_cli.add_argument(
        "-t",
        "--target",
        type=str,
        default="models.py",
        help="Target path to save models",
    )

    omm_cli.add_argument("-v", action="store_true", default=False, help="Verbose mode")

    omm_cli.add_argument(
        "--no-dump",
        action="store_true",
        default=False,
        help="Create without saving to the file. Only print result to the console.",
    )

    omm_cli.add_argument(
        "--no-global-schema",
        action="store_true",
        default=False,
        help="Define schema in table_args, not global in Gino()",
    )
    omm_cli.add_argument(
        "--defaults-off",
        action="store_true",
        default=False,
        help="Do not add defaults in Pydantic & Dataclass models",
    )
    return omm_cli


def main():
    omm = cli()
    args = omm.parse_args()

    input_path = args.ddl_file_path
    target_file = "models.py"
    if not os.path.isfile(input_path):
        print("The file path specified does not exist or it is a folder")
        sys.exit()

    print(f"Start parsing file {input_path} \n")
    result = create_models(
        ddl_path=input_path,
        dump=not args.no_dump,
        dump_path=args.target,
        models_type=args.models_type,
        schema_global=not args.no_global_schema,
        defaults_off=args.defaults_off,
    )
    print(f"File with result was saved to {target_file} file")

    if args.v or args.no_dump:
        pprint.pprint(result)
