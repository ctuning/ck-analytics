CK extensions - predictive analytics
====================================

This is a relatively stable repository used to simplify and unify
experimentation and expose it to predictive analytics
(statistical analysis, feature selection, machine learning).

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

* Grigori Fursin, cTuning foundation (France) / dividiti (UK)

License
=======
* BSD, 3-clause

Installation
============

> ck pull repo:ck-analytics

Modules
=======

experiment                           (ck-analytics)                    universal experiment entries
  * add
  * convert_table_to_csv
  * delete_points
  * filter
  * get
  * get_all_meta
  * html_viewer
  * list_points
  * load_point
  * multi_stat_analysis
  * replay
  * reproduce
  * rerun
  * sort_table
  * stat_analysis
  * substitute_x_with_loop

experiment.view                      (ck-analytics)                    customizable views for experiments

graph                                (ck-analytics)                    universal graphs for experiments
  * continuous_plot
  * html_viewer
  * plot
  * replay

graph.dot                            (ck-analytics)                    .dot graphs (graphviz - useful ot customize decision trees from predictive analytics)
  * convert_to_decision_tree

math.frontier                        (ck-analytics)                    detecting (Pareto) frontier for multi-objective optimizations
  * filter

math.variation                       (ck-analytics)                    analyzing variation of experimental results (min,max,average,expected values,etc)
  * analyze

model                                (ck-analytics)                    universal predictive modeling
  * build
  * convert_to_csv
  * use
  * validate

model.r                              (ck-analytics)                    predictive modeling via R
  * build
  * validate

model.sklearn                        (ck-analytics)                    predictive modeling via python-based scikit-learn
  * build
  * convert_categories_to_floats
  * validate

report                               (ck-analytics)                    preparing experimental reports (html)
  * html_viewer

table                                (ck-analytics)                    preparing experimental tables (txt,html)
  * draw
