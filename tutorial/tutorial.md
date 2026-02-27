# q2-qSIP2 tutorial

## Overview

This tutorial explains how to use `q2-qsip2` to analyze data generated with quantitative stable isotope probing (qSIP).
`q2-qsip2` makes the functionality developed in the qSIP2 R package available to QIIME 2 users as plugin.
The qSIP2 R package is available [here](https://github.com/jeffkimbrel/qSIP2).
The accompanying documentation for  the qSIP2 R package is available [here](https://jeffkimbrel.github.io/qSIP2/).

Stable isotope probing (SIP) is defined by Wikipedia to be:

> [...] a technique in microbial ecology for tracing uptake of nutrients in biogeochemical cycling by microorganisms.
> A substrate is enriched with a heavier stable isotope that is consumed by the organisms to be studied.

If we choose a substrate whose components are incorporated into newly synthesized DNA in a living organism we can use DNA as a biomarker for activity.
In the lab we extract this DNA and separate it according to density, into what are called "fractions".
By sequencing each of these fractions separately and classifying the taxa present in each fraction, we can answer a large number of interesting questions.

*Quantitative* stable isotope probing uses the same fundamental techniques as SIP but additionally quantifies two crucial variables:

- the extent to which organisms have incorporated the labeled isotope, by
measuring the density of each fraction
- the amount of DNA in each fraction

This allows us to precisely measure to the degree of activity of each organism identified in the sample.


## Pre-processing to prepare data for use with q2-qsip2

Commonly, qSIP data is composed of two distinct collections of data:

- the study metadata, containing the quantification data
- a feature table, containing relative abundances for all taxa identified in
all samples

The qSIP2 plugin assumes that you have both of these things already.
If your data is in an earlier stage, for example if you have reads fresh off the sequencer, you can go to the [QIIME 2 documentation](https://amplicon-docs.qiime2.org/en/stable/) to learn about how to import your data in QIIME 2.
The [Moving Pictures Tutorial](https://docs.qiime2.org/2024.5/tutorials/moving-pictures/) shows you how to go from raw sequencing data to a feature table (and beyond).

If your data is in a completely different format or set of formats, please reach out to us on the [QIIME 2 Forum](https://forum.qiime2.org) for help.

## Getting started with q2-qsip2

Once you have the above data, there are a couple of things you have to do before barreling ahead with `q2-qsip2`.
The first is to make sure that your feature table is stored in a QIIME 2 artifact.
The [importing documentation](https://docs.qiime2.org/2024.5/tutorials/importing/#feature-table-data) can help you with this, if you didn't create your feature table with QIIME 2.

The second is to understand which of two forms your study metadata is in.
The metadata structure of qSIP data is somewhat more complicated than that of more typical 16S sequencing workflows.
That is because qSIP metadata is hierarchical.
There are "source" level entities--these are commonly the subjects in your study, and represent a single microbial community, whether enriched with the heavy isotope or unenriched.
Then there are "sample" level entities--these are the individual fractions that are separated from a single source and then sequenced individually.
Thus there are multiple samples per source, and study metadata must take this into account.

There are two ways to store such hierarchical metadata: in a single file, or in two files, where one represents the source-level metadata and the other the sample-level metadata.
The `q2-qSIP2` plugin accepts either format.

### Required Metadata

There is a core set of metadata that the qSIP2 plugin requires.
These are presented as individual metadata columns with a brief explanation below.

- An **isotope** column.
  This column details, for each source, whether it was enriched with the heavy isotope or whether it was not enriched and thus has the light isotope.
  The heavy and light isotopes are sometimes referred to as "labeled" and "unlabeled", respectively.
- An **isotopolog** column.
  This column details, for each source, which isotoplog was used for enrichment.
  It is not uncommon for all sources to have the same isotopolog.
- A **gradient position** column.
  This column details, for each sample, which gradient position it corresponds to, that is, which fraction the sample represents.
- A **gradient position density** column.
  This column details the density of each sample (fraction).
- A **gradient position amount** column.
  This column details the amount of DNA in each sample (fraction).

In addition to the above lab-related columns this one further column that `q2-qsip2` must be made aware of:

- A **source material id** column.
  This column details, for each sample, which source-level entity it corresponds to.
  This column must be present whether one or two metadata files are provided as input.

## Standardizing the Metadata

The first step is to standardize the study metadata.
This includes renaming important metadata variables and condensing separate source-level and sample-level metadata files (if present) into a single file.

The tutorial data contains such separated source-level and sample-level metadata.
The `source.tsv`, and `sample.tsv` files are located in [the same directory as this tutorial](https://github.com/colinvwood/q2-qsip2/blob/main/tutorial).

```shell
qiime qsip2 standardize-metadata \
  --m-sample-metadata-file sample.tsv \
  --m-source-metadata-file source.tsv \
  --p-source-mat-id-column source \
  --p-isotope-column Isotope \
  --p-gradient-position-column Fraction \
  --p-gradient-pos-density-column density_g_ml \
  --p-gradient-pos-amt-column avg_16S_g_soil \
  --o-standardized-metadata standardized-md.qza
```

**Important**: When working with your own data, if you have a single metadata file, the software treats this a sample-level metadata, and you would simply not provide the `--p-source-metadata` argument in your call to `standardize-metadata`.

Each of the column names has a default value that can be seen by running `qiime qsip2 standardize-metadata --help` and reading the resulting command line output.
If a column in your metadata is already named with this default then you do not need to provide that argument.
For example, if your **source material id** column is alread called `source_mat_id` you can drop the `--p-source-mat-id` argument from the command.
Note that in this example we are dropping the `--p-isotoplog-column` argument from the command because our isotoplog column is already named with the default.

## Checking for Outlier Fractions

An initial quality control check one may want to perform is to look for fractions with abnormal density values.
One way of doing so is by plotting fraction position by fraction density.
Because fractions are created in a measured, linear manner, we expect these points to fall along a straight line and can visually scan for any that don't.
These can then be filtered from the dataset or redone in the lab.

```shell
qiime qsip2 plot-density-outliers \
  --m-metadata-file standardized-md.qza \
  --o-visualization density-outliers.qzv
```

Visualizations can be viewed by using [QIIME 2 View](https://view.qiime2.org) or running `qiime tools view <visualization.qzv>` from the command line.

## Calculating Source-Level Weighted Average Densities

An initial question we might have about our data is, how much denser are our enriched sources compared to our unenriched sources?
This gives us a rough feel of the relative extents to which there is evidence of activity in our enriched samples.
To answer this question we calculate per-source weighted average densities as follows.

```shell
qiime qsip2 calculate-source-WADs \
  --i-table feature-table.qza \
  --m-metadata-file standardized-md.qza \
  --o-source-wads source-wads.qza
```

These can then be visualized with:

```shell
qiime qsip2 plot-source-WADs \
  --i-source-wads source-wads.qza \
  --m-metadata-file standardized-md.qza \
  --p-group Moisture \
  --o-visualization source-wads.qzv
```

The `--p-group` parameter can be any source-level metadata column that you want to use to facet the resulting plot of weighted average densities (WADs).
Here, we are interested in seeing if activity differs between our two moisture groups, "normal" and "drought".

Another quality control visualization involves plotting DNA amount against sample density within each source.

```shell
qiime qsip2 plot-density-distributions \
  --i-table feature-table.qza \
  --m-metadata-file standardized-md.qza \
  --o-visualization density-distributions.qzv
```

## Calculating Feature-Level Weighted Average Densities

Next we will begin to answer the following overarching question of a qSIP analysis: which microorganisms are differentially active between experimental groups of interest?
To do so we will calculate weighted average densities for each feature in each source.
This weighted density is caluclated as the abundance-weighted mean of the sample densities that a feature is present in.

```shell
qiime qsip2 calculate-feature-WADs \
  --i-table feature-table.qza \
  --m-metadata-file standardized-md.qza \
  --p-unlabeled-isotope '12C' \
  --p-labeled-isotope '13C' \
  --p-min-unlabeled-sources 1 \
  --p-min-labeled-sources 1 \
  --p-min-unlabeled-fractions 2 \
  --p-min-labeled-fractions 2 \
  --o-filtered-table filtered-table.qza \
  --o-feature-wads feature-wads.qza
```

This action first filters the feature table to only those features that meet certain prevalence requirements.
First, the `--p-min-[un]lableled-fractions` parameters define the number of fractions a feature must be present in to be considered present in the entire source.
Next, the `--p-min-[un]labeled-sources` parameters define the number of sources of each isotope type a feature must be found in to be retained in the feature table and to have a WAD calculated for it.
The `--p-[un]labeled-isotope` parameters define the isotope metadata variable values that correspond to each of the two isotope categories.
It is assumed that all sources present in each of these categories are intended to be part of the analysis; if this is not the case then the metadata and feature table should be filtered first.

To inspect the amount of filtering that has been performed we can use the following visualization, which shows overall and per-source feature retention.

```shell
qiime qsip2 plot-filtering-results \
  --i-unfiltered-table feature-table.qza \
  --i-filtered-table filtered-table.qza \
  --m-metadata-file standardized-md.qza \
  --o-visualization filtering-results.qzv
```

## Calculating Excess Atom Fractions

Next we are ready to calculate excess atom fractions (EAFs), which are quantities defined at the feature level that represent the extent to which a feature incorporated the labeled isotope.
An EAF of 0 means that no incorporation was measured and an EAF of 1 means that total incorporation was measured.
This fraction is thus a proxy for activity of that feature in its source's community.

```shell
qiime qsip2 calculate-feature-EAFs \
  --i-table filtered-table.qza \
  --i-feature-wads feature-wads.qza \
  --m-metadata-file standardized-md.qza \
  --p-unlabeled-isotope 12C \
  --p-labeled-isotope 13C \
  --p-allow-resampling-failures \
  --o-feature-eafs feature-eafs.qza
```

The `--p-resamples` argument gives the number of bootstrap samples to perform when sampling the per-taxon WADs.
The `--p-random-seed` argument simply exposes the seed to the internally used random number generator.
Setting this to the same value across multiple runs yields consistent results.
The `--p-allow-resampling-failures` parameter allows all-NA bootstrapped samples of weighted average densities to be discarded, instead of throwing an error.
A consequence of enabling this parameter is that some features may have fewer than `--p-resamples` samples informing their EAF confidence interval.

We can visualize these EAFs using the following command.

```shell
qiime qsip2 plot-feature-EAFs \
  --i-feature-eafs feature-eafs.qza \
  --p-num-top 10 \
  --o-visualization feature-eafs.qzv
```

The `--p-num-top` parameter gives the number of features to show in the plot, selected from the largest EAF values.
The `--p-confidence-interval` gives the interval of bootstrapped EAFs to display in the plot.
