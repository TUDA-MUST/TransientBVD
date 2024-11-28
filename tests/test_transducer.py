import unittest
from transientbvd import predefined_transducer, predefined_transducers, Transducer


class TestTransducerModule(unittest.TestCase):
    def test_predefined_transducers(self):
        """Test that predefined_transducers() returns a non-empty list."""
        transducer_names = predefined_transducers()
        self.assertIsInstance(transducer_names, list)
        self.assertGreater(len(transducer_names), 0)  # Ensure there are transducers
        for name in transducer_names:
            self.assertIsInstance(name, str)  # Ensure all names are strings

    def test_predefined_transducer_valid(self):
        """Test retrieving any valid transducer."""
        transducer_names = predefined_transducers()
        for name in transducer_names:
            transducer = predefined_transducer(name)
            self.assertIsInstance(transducer, Transducer)
            self.assertEqual(transducer.name, name)

    def test_predefined_transducer_invalid(self):
        """Test retrieving an invalid transducer name."""
        with self.assertRaises(ValueError) as context:
            predefined_transducer("invalid_name")
        self.assertIn("Transducer 'invalid_name' not found", str(context.exception))

    def test_parameters_method(self):
        """Test the parameters() method of each transducer."""
        transducer_names = predefined_transducers()
        for name in transducer_names:
            transducer = predefined_transducer(name)
            parameters = transducer.parameters()
            self.assertIsInstance(parameters, tuple)
            self.assertEqual(len(parameters), 4)
            self.assertTrue(all(isinstance(param, float) for param in parameters))

    def test_str_method(self):
        """Test the __str__ method of each transducer."""
        transducer_names = predefined_transducers()
        for name in transducer_names:
            transducer = predefined_transducer(name)
            transducer_str = str(transducer)
            self.assertIn(name, transducer_str)  # Ensure the name appears in the string

    def test_repr_method(self):
        """Test the __repr__ method of each transducer."""
        transducer_names = predefined_transducers()
        for name in transducer_names:
            transducer = predefined_transducer(name)
            transducer_repr = repr(transducer)
            self.assertIn(name, transducer_repr)  # Ensure the name appears in the representation
            self.assertTrue(transducer_repr.startswith("Transducer("))  # Check format


if __name__ == "__main__":
    unittest.main()
