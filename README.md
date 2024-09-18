# q2-qsip2

A [QIIME 2](https://qiime2.org) plugin [developed](https://develop.qiime2.org) by Colin Wood (colin.wood@nau.edu). 🔌

## Installation instructions

### Install Prerequisites

[Miniconda](https://conda.io/miniconda.html) provides the `conda` environment and package manager, and is currently the only supported way to install QIIME 2.
Follow the instructions for downloading and installing Miniconda.

After installing Miniconda and opening a new terminal, make sure you're running the latest version of `conda`:

```bash
conda update conda
```

###  Install development version of `q2-qsip2`

Next, you need to get into the top-level `q2-qsip2` directory.
You can achieve this by [cloning the repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository), for example with the command:

```shell
git clone https://github.com/colinvwood/q2-qsip2.git
```

Once you have the directory on your computer, change (`cd`) into it.

If you're in a conda environment, deactivate it by running `conda deactivate`.

Then, run:

```shell
conda env create -n q2-qsip2-dev --file ./environments/q2-qsip2-qiime2-amplicon-2024.5.yml
```

After this completes, activate the new environment you created by running:

```shell
conda activate q2-qsip2-dev
```

Finally, run:

```shell
make install
```

## Testing and using the most recent development version of `q2-qsip2`

After completing the install steps above, confirm that everything is working as expected by running:

```shell
make test
```

You should get a report that tests were run, and you should see that all tests passed and none failed.
It's usually ok if some warnings are reported.

If all of the tests pass, you're ready to use the plugin.
Start by making QIIME 2's command line interface aware of `q2-qsip2` by running:

```shell
qiime dev refresh-cache
```

You should then see the plugin in the list of available plugins if you run:

```shell
qiime info
```

You should be able to review the help text by running:

```shell
qiime qsip2 --help
```

## Accessing the usage tutorial

You can find instructions for performing an example analysis with q2-qsip2 in the [tutorial](https://github.com/colinvwood/q2-qsip2/blob/main/tutorial/tutorial.md).
The data files that you'll need to run that tutorial can be downloaded from [the directory containing the tutorial](https://github.com/colinvwood/q2-qsip2/tree/main/tutorial).

Have fun! 😎

## About

The `q2-qsip2` Python package was [created from template](https://develop.qiime2.org/en/latest/plugins/tutorials/create-from-template.html).
To learn more about `q2-qsip2`, refer to the [project website](www.qiime2.org).
To learn how to use QIIME 2, refer to the [QIIME 2 User Documentation](https://docs.qiime2.org).
To learn QIIME 2 plugin development, refer to [*Developing with QIIME 2*](https://develop.qiime2.org).

`q2-qsip2` is a QIIME 2 community plugin, meaning that it is not necessarily developed and maintained by the developers of QIIME 2.
Please be aware that because community plugins are developed by the QIIME 2 developer community, and not necessarily the QIIME 2 developers themselves, some may not be actively maintained or compatible with current release versions of the QIIME 2 distributions.
More information on development and support for community plugins can be found [here](https://library.qiime2.org).
If you need help with a community plugin, first refer to the [project website](www.qiime2.org).
If that page doesn't provide information on how to get help, or you need additional help, head to the [Community Plugins category](https://forum.qiime2.org/c/community-contributions/community-plugins/14) on the QIIME 2 Forum where the QIIME 2 developers will do their best to help you.
