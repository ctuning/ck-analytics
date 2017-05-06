import ck.kernel as ck

scenario='experiment.tune.compiler.flags.gcc.e'
compiler='GCC 7.1.0'
cpu_name='BCM2709'

features= ["9.0", "4.0", "2.0", "0.0", "5.0", "2.0", "0.0", "4.0", "0.0", "0.0", "2.0", "0.0", "7.0", "0.0", "0.0", 
           "10.0", "0.0", "0.0", "1.0", "2.0", "10.0", "4.0", "1.0", "14.0", "2.0", "0.714286", 
           "1.8", "3.0", "0.0", "4.0", "0.0", "3.0", "0.0", "3.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "2.0", 
           "0.0", "1.0", "0.0", "1.0", "5.0", "10.0", "2.0", "0.0", "32.0", "0.0", "10.0", "0.0", "0.0",
           "0.0", "0.0", "3.0", "33.0", "12.0", "32.0", "93.0", "14.0", "19.25", "591.912", "11394.3"]

r=ck.access({'action':'ask',
             'module_uoa':'advice',
             'to':'predict_compiler_flags',
             'scenario':scenario,
             'compiler':compiler,
             'cpu_name':cpu_name,
             'features':features})
if r['return']>0: ck.err(r)

ck.out('Predicted optimization: '+r['predicted_opt'])
