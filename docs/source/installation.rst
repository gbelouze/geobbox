Installation
============

Installation of the `GeoBbox` package is complicated by its dependency on `rasterio` which itself
depends on `libgdal` and other C libraries. See
https://rasterio.readthedocs.io/en/stable/installation.html for more details on installing rasterio.

Example with `conda`
--------------------

You must first ensure that `GDAL` is available on your system

.. code-block:: console

    conda install gdal

Then, install normally from PyPI

.. code-block:: console

    pip install geobbox

.. note::

    GeoBbox requires Rasterio 1.4 or higher, which requires Python 3.9 or higher and GDAL 3.3 or
    higher.

For developpers
---------------

If you want to work on `GeoBbox`, clone the repository locally and optionally install the `[doc]`
and `[dev]` dependencies.

.. code-block:: console

    git clone git@github.com:gbelouze/geobbox.git
    cd geobbox
    conda env create -f environment.yml
    pip install -e '.[dev, doc]'
