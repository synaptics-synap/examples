from typing import Optional
import json
import zipfile

from utils.common import INF_META_FILE


def get_model_input_dims(model: str) -> Optional[tuple[int, int]]:
    """
    Attempts to find model input dimensions by parsing .synap file.
    """
    try:
        with zipfile.ZipFile(model, "r") as mod_info:
            if INF_META_FILE not in mod_info.namelist():
                raise FileNotFoundError("Missing model metadata")
            with mod_info.open(INF_META_FILE, "r") as meta_f:
                metadata = json.load(meta_f)
                inputs = metadata["Inputs"]
                if len(inputs) > 1:
                    raise NotImplementedError("Multiple input models not supported")
                input_info = inputs[list(inputs.keys())[0]]
                if input_info["format"] == "nhwc":
                    inp_w, inp_h = input_info["shape"][2], input_info["shape"][1]
                elif input_info["format"] == "nchw":
                    inp_w, inp_h = input_info["shape"][3], input_info["shape"][2]
                else:
                    raise ValueError(
                        f"Invalid metadata: unknown format \"{input_info['format']}\""
                    )
                # print(f"Extracted model input size: {inp_w}x{inp_h}")
                return inp_w, inp_h
    except (zipfile.BadZipFile, FileNotFoundError):
        print(f"\nInvalid SyNAP model: {model}\n")
    except KeyError as e:
        print(f'\nMissing model metadata "{e.args[0]}"\nInvalid SyNAP model: {model}\n')
    except (NotImplementedError, ValueError) as e:
        print(f"\n{e.args[0]}\nInvalid SyNAP model: {model}\n")
