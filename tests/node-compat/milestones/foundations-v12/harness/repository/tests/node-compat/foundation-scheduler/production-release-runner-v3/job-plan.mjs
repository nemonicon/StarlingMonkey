import {join} from 'node:path';
export function releaseJobs(here,output){
  return[
    {name:'core',runner:join(here,'../production-regression-candidate-v5/run-core.mjs'),variable:'NODE_COMPAT_OUTPUT',report:'results.json',completion:'production-admission-complete.json'},
    {name:'allocator',runner:join(here,'../production-regression-candidate-v5/run-allocator.mjs'),variable:'NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT',report:'results.json',completion:'production-admission-complete.json'},
    {name:'stream-web',runner:join(here,'../production-followon-off-v3/run-stream-web.mjs'),variable:'NODE_COMPAT_STREAM_WEB_OUTPUT',report:'results.json',completion:'followon-admission-complete.json'},
    {name:'optional',runner:join(here,'run-optional.mjs'),variable:'NODE_COMPAT_OPTIONAL_OUTPUT',report:'results.json',completion:'release-admission-complete.json'},
    ...['sync','runtime','late','callbacks'].map(name=>({name:'strict-'+name,runner:join(here,'../production-followon-off-v3/run-'+name+'.mjs'),
      variable:'NODE_COMPAT_STRICT_EVENT_OUTPUT',report:'private-ticks-'+(name==='callbacks'?'callback':name)+'-results.json',completion:'followon-admission-complete.json'})),
  ].map(job=>({...job,output:join(output,job.name)}));
}
