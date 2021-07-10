Unifying predictive analytics with the CK JSON API
==================================================

**All CK components can be found at [cKnowledge.io](https://cKnowledge.io) and in [one GitHub repository](https://github.com/ctuning/ck-mlops)!**

*This project is hosted by the [cTuning foundation](https://cTuning.org).*

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](http://cTuning.org/ae)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

This is a [Collective Knowledge](https://github.com/ctuning/ck) repository
containing CK modules and actions to unify the access to different predictive 
analytics frameworks (scipy, R, DNN) using our standard CK JSON API. 

The community use it research workflows/pipelines to enable 
collaborative, reusable and reproducible experimentation.

See our recent papers for more details: 
[1](https://cKnowledge.io/report/rpi3-crowd-tuning-2017-interactive), 
[2](https://arxiv.org/abs/2001.07935).

Further info:
* [Open CK platform to publish and download stable CK components](https://cKnowledge.io)
* [Documentation about portable CK workflows](https://github.com/ctuning/ck/wiki/Portable-workflows)
* [Shared portable CK program workflows](https://cKnowledge.io/programs)
* [Related CK publications](https://github.com/ctuning/ck/wiki/Publications)

Author
======
* [Grigori Fursin](https://fursin.net)

Contributors
============
* See the list of [contributors](https://github.com/ctuning/ck-analytics/blob/master/CONTRIBUTIONS)

Shared CK modules with actions
==============================

* [advice](https://cKnowledge.io/c/module/advice)
* [experiment](https://cKnowledge.io/c/module/experiment)
* [experiment.raw](https://cKnowledge.io/c/module/experiment.raw)
* [experiment.view](https://cKnowledge.io/c/module/experiment.view)
* [graph](https://cKnowledge.io/c/module/graph)
* [graph.dot](https://cKnowledge.io/c/module/graph.dot)
* [jnotebook](https://cKnowledge.io/c/module/jnotebook)
* [math.conditions](https://cKnowledge.io/c/module/math.conditions)
* [math.frontier](https://cKnowledge.io/c/module/math.conditions)
* [math.variation](https://cKnowledge.io/c/module/math.variation)
* [model](https://cKnowledge.io/c/module/model)
* [model.image.classification](https://cKnowledge.io/c/module/model.image.classification)
* [model.r](https://cKnowledge.io/c/module/model.r)
* [model.sklearn](https://cKnowledge.io/c/module/model.sklearn)
* [model.species](https://cKnowledge.io/c/module/model.species)
* [model.tf](https://cKnowledge.io/c/module/model.tf)
* [report](https://cKnowledge.io/c/module/report)
* [table](https://cKnowledge.io/c/module/table)

Installation
============

First install the CK framework as described [here](https://github.com/ctuning/ck#installation).

Then install this CK repository as follows:

```
 $ ck pull repo:ck-analytics

 $ ck list ck-analytics:module:*

```

Dependencies
============

Python:
* matplotlib
* scipy
* numpy
* sklearn-kit

OS:
* Graphviz

On Ubuntu, you can install packages using:
```
$ sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas graphviz
```

On Windows you can use pip to install dependencies:
```
$ pip install matplotlib scipy numpy sklearn-kit
```

You can download Graphviz for Windows from this [website](http://www.graphviz.org/Download_windows.php), install it and add it to the PATH. 

Extra functionality (some machine learning functions):

* R (for statistical analysis and machine learning, though Python may be enough)

* TensorFlow (will be installed automatically by CK)


Usage
=====

Please, check various examples with JSON API and meta information 
in the [demo directory](https://github.com/ctuning/ck-analytics/tree/master/demo).

CK AI JSON API
==============

We provide unfied JSON API for self-optimizing DNN:
* Demo: http://cknowledge.org/repo/web.php?template=ck-ai-basic
* Wiki: https://github.com/ctuning/ck/wiki/Unifying-AI-API

Questions and comments
======================

Please feel free to get in touch with the [CK community](https://github.com/ctuning/ck/wiki/Contacts) 
if you have any questions, suggestions and comments!
