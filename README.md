This Collective Knowledge extension repository contains CK modules 
to unify access to various predictive analytics engines (scipy, R, DNN) 
from software, command line and web-services via CK JSON API: http://cKnowledge.org/ai

We use it in our [open research](https://github.com/ctuning/ck/wiki/Enabling-open-science) 
to simplify and unify experimentation such as collaborative optimization of computer systems
and DNN across diverse hardware and software, and expose it to predictive analytics
(statistical analysis, feature selection, machine learning).

Prerequisites
=============
* Collective Knowledge Framework: http://github.com/ctuning/ck

Dependencies
============

Python:
* matplotlib
* scipy
* numpy
* sklearn-kit

On Ubuntu, you can install packages using:
> sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas

Useful:

* Graphviz
* R (for statistical analysis and machine learning, though Python may be enough)

Authors
=======

* [Grigori Fursin](http://fursin.net/research.html), cTuning foundation/dividiti

License
=======
* BSD, 3-clause

Installation
============

> ck pull repo:ck-analytics

Please, check various examples with JSON API and meta information 
in the [demo directory](https://github.com/ctuning/ck-analytics/tree/master/demo).

Modules with actions
====================

experiment - universal experiment entries

  * add - process and add experiment
  * convert_table_to_csv - Convert experiment table to CSV
  * delete_points - delete multiple points from multiple entries
  * filter - filter / pre-process data
  * get - get points from multiple entries
  * get_all_meta - get all meta information from all entries
  * html_viewer - view experiment as html
  * list_points - list all points in a given entry
  * load_point - load all info about a given point (and subpoint)
  * multi_stat_analysis - perform statistical analysis (with multiple points at the same time)
  * replay - replay experiment == the same as reproduce
  * reproduce - reproduce/replay/rerun a given experiment
  * rerun - rerun experiment == the same as reproduce
  * sort_table - sort table, substitute index with a sequence (html)
  * stat_analysis - process multiple experimental results and perform statistical analysis (including expected values)
  * substitute_x_with_loop - substitute x axis in table with a sequence

experiment.view - customizable views for experiments

graph - universal graphs for experiments

  * continuous_plot - update plot periodically (useful to demonstrate continuous experiments and active learning)
  * html_viewer - view graph in html
  * plot - plot graph
  * replay - replay saved graph (to always keep default graphs for interactive papers)

graph.dot - .dot graphs (graphviz - useful to customize decision trees from predictive analytics)

  * convert_to_decision_tree - convert .dot file a universal decision tree (useful before converting into C code for adaptive applications and libraries)

math.frontier - detecting (Pareto) frontier for multi-objective optimizations

  * filter - filter experiments with multiple characteristics (performance, energy, accuracy, size, etc) to leave only points on a (Pareto) frontier

math.variation - analyzing variation of experimental results (min,max,average,expected values,etc)

  * analyze - analyze variation of experimental results including multiple expected values

model - universal predictive modeling

  * build - build predictive model
  * convert_to_csv - convert table to CSV
  * use - use existing model to predict values
  * validate - validate predictive model (detect mispredictions, calculate RMSE, etc)

model.r - predictive modeling via R

  * build - build predictive model
  * validate - validate predictive model

model.sklearn - predictive modeling via python-based scikit-learn

  * build - build predictive model
  * convert_categories_to_floats - convert categories to floats
  * validate - validate predictive model

report - preparing experimental reports (html)

  * html_viewer - view report as html

table - preparing experimental tables (txt,html)

  * draw - draw experiment table (in txt or html)

Publications
============

```
@inproceedings{ck-date16,
    title = {{Collective Knowledge}: towards {R\&D} sustainability},
    author = {Fursin, Grigori and Lokhmotov, Anton and Plowman, Ed},
    booktitle = {Proceedings of the Conference on Design, Automation and Test in Europe (DATE'16)},
    year = {2016},
    month = {March},
    url = {https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability}
}

@inproceedings{cm:29db2248aba45e59:cd11e3a188574d80,
    title = {{Collective Mind, Part II}: Towards Performance- and Cost-Aware Software Engineering as a Natural Science},
    author = {Fursin, Grigori and Memon, Abdul and Guillon, Christophe and Lokhmotov, Anton},
    booktitle = {18th International Workshop on Compilers for Parallel Computing (CPC'15)},
    year = {2015},
    url = {https://arxiv.org/abs/1506.06256},
    month = {January}
}

@inproceedings{Fur2009,
  author =    {Grigori Fursin},
  title =     {{Collective Tuning Initiative}: automating and accelerating development and optimization of computing systems},
  booktitle = {Proceedings of the GCC Developers' Summit},
  year =      {2009},
  month =     {June},
  location =  {Montreal, Canada},
  keys =      {http://www.gccsummit.org/2009}
  url  =      {https://scholar.google.com/citations?view_op=view_citation&hl=en&user=IwcnpkwAAAAJ&cstart=20&citation_for_view=IwcnpkwAAAAJ:8k81kl-MbHgC}
}
```

* http://arxiv.org/abs/1506.06256
* http://hal.inria.fr/hal-01054763
* https://hal.inria.fr/inria-00436029
* http://arxiv.org/abs/1407.4075
* https://scholar.google.com/citations?view_op=view_citation&hl=en&user=IwcnpkwAAAAJ&citation_for_view=IwcnpkwAAAAJ:LkGwnXOMwfcC

Feedback
========

If you have problems, questions or suggestions, do not hesitate to get in touch
via the following mailing lists:
* https://groups.google.com/forum/#!forum/collective-knowledge
* https://groups.google.com/forum/#!forum/ctuning-discussions

![logo](https://github.com/ctuning/ck-guide-images/blob/master/logo-validated-by-the-community-simple.png)
