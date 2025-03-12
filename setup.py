from setuptools import setup

setup(
    name="TransientBVD",
    version="0.1.0",
    description="A Python library for transient response analysis and optimization of resonant "
    "systems modeled by the Butterworth-Van Dyke (BVD) equivalent circuit.",
    long_description=(
        "TransientBVD enables advanced transient analysis of ultrasound transducers "
        "and other resonant systems. It supports both deactivation (resistive damping) "
        "and activation (voltage overboost) strategies for rapid transient control."
    ),
    author="Jan Helge Dörsam",
    packages=["transientbvd"],
)
