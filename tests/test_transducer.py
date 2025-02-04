import json
import tempfile
import unittest
from unittest.mock import patch

from transientbvd import (
    select_transducer,
    predefined_transducers,
    Transducer,
    load_transducers,
)


class TestTransducerModule(unittest.TestCase):
    @patch(
        "transientbvd.transducer.load_measured_transducers",
        return_value={
            "SMBLTD45F40H_1": Transducer(
                rs=21.05, ls=35.15e-3, cs=448.62e-12, c0=4075.69e-12
            )
            .set_name("SMBLTD45F40H_1")
            .set_manufacturer("STEINER & MARTINS INC., Davenport, USA"),
            "GB-4540-4SH": Transducer(rs=17.2, ls=32.52e-3, cs=464.1e-12, c0=3.397e-9)
            .set_name("GB-4540-4SH")
            .set_manufacturer("Granbo Ultrasonic, Shenzhen, China"),
        },
    )
    def test_predefined_transducers(self, mock_load):
        """Test that predefined_transducers() returns a non-empty dictionary."""
        transducer_dict = predefined_transducers()
        self.assertIsInstance(transducer_dict, dict)  # Expect a dictionary
        self.assertGreater(len(transducer_dict), 0)  # Ensure there are transducers
        for name, transducer in transducer_dict.items():
            self.assertIsInstance(name, str)  # Ensure keys (names) are strings
            self.assertIsInstance(
                transducer, Transducer
            )  # Ensure values are Transducer objects

    @patch(
        "transientbvd.transducer.load_measured_transducers",
        return_value={
            "SMBLTD45F40H_1": Transducer(
                rs=21.05, ls=35.15e-3, cs=448.62e-12, c0=4075.69e-12
            )
            .set_name("SMBLTD45F40H_1")
            .set_manufacturer("STEINER & MARTINS INC., Davenport, USA")
        },
    )
    def test_predefined_transducer_valid(self, mock_load):
        """Test retrieving any valid transducer."""
        transducer = select_transducer("SMBLTD45F40H_1")
        self.assertIsInstance(transducer, Transducer)
        self.assertEqual(transducer.name, "SMBLTD45F40H_1")

    @patch("transientbvd.transducer.load_measured_transducers", return_value={})
    def test_predefined_transducer_invalid(self, mock_load):
        """Test retrieving an invalid transducer name."""
        with self.assertRaises(ValueError) as context:
            select_transducer("invalid_name")
        self.assertIn("Transducer 'invalid_name' not found", str(context.exception))

    @patch(
        "transientbvd.transducer.load_measured_transducers",
        return_value={
            "SMBLTD45F40H_1": Transducer(
                rs=21.05, ls=35.15e-3, cs=448.62e-12, c0=4075.69e-12
            )
            .set_name("SMBLTD45F40H_1")
            .set_manufacturer("STEINER & MARTINS INC., Davenport, USA")
        },
    )
    def test_str_method(self, mock_load):
        """Test the __str__ method of each transducer."""
        transducer = select_transducer("SMBLTD45F40H_1")
        transducer_str = str(transducer)
        self.assertIn(
            "SMBLTD45F40H_1", transducer_str
        )  # Ensure the name appears in the string

    @patch(
        "transientbvd.transducer.load_measured_transducers",
        return_value={
            "SMBLTD45F40H_1": Transducer(
                rs=21.05, ls=35.15e-3, cs=448.62e-12, c0=4075.69e-12
            )
            .set_name("SMBLTD45F40H_1")
            .set_manufacturer("STEINER & MARTINS INC., Davenport, USA")
        },
    )
    def test_repr_method(self, mock_load):
        """Test the __repr__ method of each transducer."""
        transducer = select_transducer("SMBLTD45F40H_1")
        transducer_repr = repr(transducer)
        self.assertIn(
            "SMBLTD45F40H_1", transducer_repr
        )  # Ensure the name appears in the representation
        self.assertTrue(transducer_repr.startswith("Transducer("))  # Check format


class TestJSONLoading(unittest.TestCase):
    def test_load_transducers(self):
        """Test loading transducers from a JSON file."""
        # Create a temporary JSON file with test data
        test_data = {
            "SMBLTD45F40H_1": {
                "rs": 21.05,
                "ls": 0.03515,
                "cs": 4.4862e-10,
                "c0": 4.07569e-9,
                "manufacturer": "STEINER & MARTINS INC., Davenport, USA",
            }
        }
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            json.dump(test_data, temp_file)
            temp_file_path = temp_file.name

        # Load transducers from the temporary JSON file
        transducers = load_transducers(temp_file_path)

        # Check that the transducer is loaded correctly
        self.assertIn("SMBLTD45F40H_1", transducers)
        transducer = transducers["SMBLTD45F40H_1"]
        self.assertIsInstance(transducer, Transducer)
        self.assertEqual(transducer.name, "SMBLTD45F40H_1")
        self.assertAlmostEqual(transducer.rs, 21.05)


if __name__ == "__main__":
    unittest.main()
