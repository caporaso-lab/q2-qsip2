# q2-qSIP2 tutorial

## Overview

This tutorial explains how to use `q2-qsip2` to analyze data generated
with quantitative stable isotope probing (qSIP). This software makes the
functionality developed in the qSIP2 R package available to QIIME2 users as
plugin. The qSIP2 R package is available
[here](https://github.com/jeffkimbrel/qSIP2). The accompanying documentation
for  the qSIP2 R package is available
[here](https://jeffkimbrel.github.io/qSIP2/).

Stable isotope probing (SIP) is defined by Wikipedia to be:

> [...] a technique in microbial ecology for tracing uptake of nutrients in
biogeochemical cycling by microorganisms. A substrate is enriched with a
heavier stable isotope that is consumed by the organisms to be studied.

If we choose a substrate whose components are incorporated into newly
synthesized DNA in a living organism we can use DNA as a biomarker
for activity. In the lab we extract this DNA and separate it according to
density, into what are called "fractions". By sequencing each of these
fractions separately and classifying the taxa present in each fraction, we can
answer a large number of interesting questions.

*Quantitative* stable isotope probing uses the same fundamental techniques as
SIP but additionally quantifies two crucial variables:

- the extent to which organisms have incorporated the labeled isotope, by
measuring the density of each fraction
- the amount of DNA in each fraction

This allows us to precisely measure to the degree of activity of each organism
identified in the sample.


## Plugging qSIP Data into QIIME2

Commonly, qSIP data is composed of two distinct collections of data:

- the study metadata, containing the quantification data
- a feature table, containing relative abundances for all taxa identified in
all samples

The qSIP2 plugin assumes that you have both of these things already. If your
data is in an earlier stage, for example if you have reads fresh off the
sequencer, you can go to the
[QIIME2 documentation](https://docs.qiime2.org/2024.5/) to learn about how
to get your data into qSIP2-accepted format. The
[Moving Pictures Tutorial](https://docs.qiime2.org/2024.5/tutorials/moving-pictures/)
shows you how to go from raw sequencing data to a feature table (and beyond).
If your data is in a completely different format or set of formats, please
reach out to us on the [QIIME2 Forum](https://forum.qiime2.org).

Once you have the above data, there are a couple of things you have to do
before barreling ahead with `q2-qsip2`. The first is to make sure that your
feature table has been imported as a QIIME2 artifact. The
[importing documentation](https://docs.qiime2.org/2024.5/tutorials/importing/#feature-table-data)
can help you with this.

The second is to understand which of two forms your study metadata is in.
The metadata structure of qSIP data is somewhat more complicated than that
of more typical 16S sequencing workflows. That is becuase qSIP metadata is
hierarchical. There are "source" level entities--these are commonly
the subjects in your study, and represent a single microbial community, whether
enriched or unenriched. Then there are "sample" level entities--these are
the individual fractions that are separated from a single source and then
sequenced individually. Thus there are multiple samples per source, and study
metadata must take this into account.

There are two ways to store such hierarchical metadata: in a single file, or in
two files, where one represents the source-level metadata and the other the
sample-level metadata. The qSIP2 plugin accepts both formats.

### Required Metadata

There is a cores set of metadata that the qSIP2 plugin requires to function.
These are presented as individual metadata columns with a brief explanation
below.

- An **isotope** column. This column details, for each source, whether it was
enriched with the heavy isotope or whether it was not enriched and thus has
the light isotope. The heavy and light isotopes are sometimes referred to as
"labeled" and "unlabeled", respectively.
- An **isotopolog** column. This column details, for each source, which isotoplog
was used for enrichment. It is not uncommon for all sources to have the same
isotopolog, but it is still crucial information for the software.
- A **gradient position** column. This column details, for each sample, which
gradient position it corresponds to, that is, which fraction the sample
represents.
- A **gradient position density** column. This column details the density of
each sample (fraction).
- A **gradient position amount** column. This column details the amount of
DNA in each sample (fraction).

In addition to the above lab-related columns this one further column
that `q2-qsip2` must be made aware of:

- A **source material id** column. This column details, for each sample, which
source-level entity it corresponds to. This column must be present whether
one or two metadata files are inputted.

### Creating a QSIP2Data Artifact

With the coneptual background out of the way, we are ready to begin our
analysis with `q2-qsip2`. The first step is to bundle our study metadata and
our feature table together into a `QSIP2Data` artifact. This artifact, or
variations of it, will be used throught the rest of the analysis. We do this
using the `create-qsip-data` command.

The `feature-table.qza`, `source.tsv`, and `sample.tsv` files are located in
the same directory as this tutorial. If you're following along with your own
data, simply plug your filenames in instead. If you have a single metadata
file, the software treats this a sample-level metadata, and you would simply
not provide the `--p-source-metadata` argument.

```shell
qiime qsip2 create-qsip-data \
  --i-table feature-table.qza \
  --m-sample-metadata-file sample.tsv \
  --m-source-metadata-file source.tsv \
  --p-source-mat-id-column source \
  --p-isotope-column Isotope \
  --p-gradient-position-column Fraction \
  --p-gradient-pos-density-column density_g_ml \
  --p-gradient-pos-amt-column avg_16S_g_soil \
  --o-qsip-data qsip-data.qza
```

Each of the column names has a default value that can be seen by running
`qiime qsip2 create-qsip-data --help` and reading the resulting command line
output. If a column in your metadata is already named with this default then
you do not need to provide that argument. For example, if your
**source material id** column is alread called `source_mat_id` you can drop
the `--p-source-mat-id` argument from the command. Note that in this example
we are dropping the `--p-isotoplog-column` argument from the command because
our isotoplog column is already named with the default. If you isotopolog
column has a different name, you should add this argument with that name.

This command results in a single output artifact: `qsip-data.qza`, which
represents both our source- and sample-level metadata, as well as our feature
table.

## Visualizing Our Initial qSIP Data

An initial question we might have about our data is, how much denser are our
enriched sources compared to our unenriched sources? This gives us a rough
feel of the relative extents to which there is evidence of activity in our
enriched samples. To visualize this, we use the following command.

```shell
qiime qsip2 plot-weighted-average-densities \
  --i-qsip-data qsip-data.qza \
  --p-group Moisture \
  --o-visualization weighted-average-densities.qzv
```

The `--p-group` command can be any source-level metadata column that you
want to use to facet the resulting plot of weighted average densities (WADs).
Here, we are interested in seeing if activity differs between our two moisture
groups, "normal" and "drought".

To view the visualization you can either go to the QIIME2 visualzation-viewer
[website](https://view.qiime2.org) and upload your file, or if your computer
has a screen (i.e. you aren't on a server), run the following on the command
line.

```shell
qiime tools view weighted-average-densities.qzv
```

Another question we might be interested in is whether there are any samples
that are outliers as far as density is concerned. Such outliers may require
reprocessing in the lab. Density should vary linearly with gradient position,
and we can visualize this with the following command.

```shell
qiime qsip2 plot-density-outliers \
  --i-qsip-data qsip-data.qza \
  --o-visualization density-outliers.qzv
```

Another quality control visualization involves plotting DNA amount against
sample density.

```shell
qiime qsip2 plot-sample-curves \
  --i-qsip-data qsip-data.qzv \
  --o-visualization sample-curves.qzv
```

## Subsetting and Filtering

Now that we have bundled our data together and performed some intitial
quality control, there is one more step we must perform before the
true analysis can begin. That step is to choose which sources and which
features to retain for analysis. To see which source IDs are available in
each of the enriched and unenriched categories we can use the following command.

```shell
qiime qsip2 show-comparison-groups \
  --i-qsip-data qsip-data.qza \
  --p-groups Moisture \
  --o-visualization comparison-groups.qzv
```

The resulting visualization will list the source IDs available in each
of the two enrichment categories, and will further divide the IDs by one or
more optional metadata columns provided to the `--p-groups` argument. If you
want to provide multiple columns simply separate them with spaces on the
command line.

This lets us make an informed decision about which sources to retain for
comparison in the next step.

Now we are ready to subset our data by keeping only sources we are interested
in and keeping only those features that meet a set of prevalence requirements.
To do so, we use the following command.

```shell
qiime qsip2 subset-and-filter \
  --i-qsip-data qsip-data.qza \
  --p-unlabeled-sources S149 S150 S151 S152 S161 S162 S163 S164 \
  --p-labeled-sources S178 S179 S180 \
  --p-min-unlabeled-sources 6 \
  --p-min-labeled-sources 3 \
  --p-min-unlabeled-fractions 6 \
  --p-min-labeled-fractions 6 \
  --o-filtered-qsip-data filtered-qsip-data.qza
```

There are four prevalence filters we can apply to the feature table. Two of
these, `--p-min-labeled-sources` and `--p-min-labeled-sources` filter features
based on their prevalence across the retained sources. The interpretation
of the values provided in the above command is that if a feature is present
in less than 6 unlabeled sources or less than 3 labeled sources, then it will
be filtered. Because we decided to retain 6 and 3 unlabeled and labeled sources
respectively, we are requiring retained features to present in *all* samples.
The other two prevalence filters, `--p-min-unlabeled-fractions` and
`--p-min-labeled-fractions` filter features based on fraction (sample)
prevalence. The interpretation of the values provided in the above command
is that if a feature is present in less than 6 fractions in an unlabeled source
or less than 6 fractions in a labeled source, then that feature is not
considered to be present in that source. This filtering thus affects the
source-based filtering, described above, which is performed subsequently.

This command outputs a single `filtered-qsip-data.qza` artifact. If we
inspect its semantic type we will see that it is a `QSIP2Data[Filtered]`
artifact. The original `qsip-data.qza` artifact was a `QSIP2Data[Unfiltered]`.
This is distinction is important because it requires our data to first be
filtered and subsetted before it's analyzed.

Now that filtering has been performed we are interested in the number of
features that have been retained, and their relative abundances. The
following command will let us visualize these questions.

```shell
qiime qsip2 plot-filtered-features \
  --i-filtered-qsip-data filtered-qsip-data.qza \
  --o-visualization filtered-features.qzv
```

The resulting visualization contains two plots. The first shows per-source
feature retention by relative abundance and the second shows per-source
feature retention by feature count. Because features have differing relative
abundances it's possible to see that a majority of features have been filtered
although a majority of feature abundance has been retained, as is the case
for the provided tutorial data.


## Calculating Excess Atom Fractions (EAFs)

We are finally ready to perform the core calculations that quanitfy relative
enrichment on a per-cfeature basis. There is a single command that performs this
process, shown below.

```shell
qiime qsip2 resample-and-calculate-EAF \
  --i-filtered-qsip-data filtered-qsip-data.qza \
  --p-resamples 2000 \
  --p-random-seed 123 \
  --o-eaf-qsip-data eaf-qsip-data.qza
```

This commands takes the filtered qSIP data object we generated above, along
with two arguments that control aspects of the underlying statistical
procedures. The `--p-resamples` argument gives the number of bootstrap
samples to perform when sampling the per-taxon WADs. The `--p-random-seed`
argument simply exposes the seed to the internally used random number
generator. Setting this to the same value across multiple runs yields
consistent results.

Each feature has now had its excess atom fraction (EAF) calculated.
This is a number in the range [0, 1] that expresses to what extent some feature
incorporated the enriched isotope. An EAF of 0 means that no incorporation
was measured and an EAF of 1 means that total incoporation was measured. This
fraction is thus a proxy for activity of that feature in its source's
community.

We can visualize these EAFs using the following command.

```shell
qiime qsip2 plot-excess-atom-fractions \
  --i-eaf-qsip-data eaf-qsip-data.qza \
  --p-num-top 25 \
  --p-confidence-interval 0.95 \
  --o-visualization excess-atom-fractions.qzv
```

This command takes two arguments beyond the input and output artifacts. The
`--p-num-top` artifact gives the number of features to show in the plot. These
are selected as the *n* features with the greatest EAFs. The
`--p-confidence-interval` gives the interval of bootstrapped EAFs to display
in the plot.
