import crypto from 'node:crypto';

const SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json';
const literal=value=>({expr:{Literal:{Value:typeof value==='boolean'?String(value):`'${String(value).replaceAll("'","''")}'`}}});
const id=seed=>crypto.createHash('sha256').update(seed).digest('hex').slice(0,20);

export function column(entity,property,label=property){return {field:{Column:{Expression:{SourceRef:{Entity:entity}},Property:property}},queryRef:`${entity}.${property}`,nativeQueryRef:property,displayName:label,active:true};}
export function measure(entity,property,label=property){return {field:{Measure:{Expression:{SourceRef:{Entity:entity}},Property:property}},queryRef:`${entity}.${property}`,nativeQueryRef:property,displayName:label,active:true};}
function base(seed,type,x,y,width,height,z){return {$schema:SCHEMA,name:id(seed),position:{x,y,width,height,z,tabOrder:z},visual:{visualType:type,visualContainerObjects:{general:[{properties:{altText:literal(seed)}}]}}};}
export function text(seed,value,x,y,width,height,z,size='18px',color='#173277',weight='600'){
  const v=base(seed,'textbox',x,y,width,height,z);v.visual.objects={general:[{properties:{paragraphs:[{textRuns:[{value,textStyle:{fontFamily:'Segoe UI',fontSize:size,color,fontWeight:weight}}],horizontalTextAlignment:'left'}]}}]};return v;
}
export function card(seed,entity,property,title,x,y,width,height,z){const v=base(seed,'cardVisual',x,y,width,height,z);v.visual.query={queryState:{Data:{projections:[measure(entity,property,title)]}}};v.visual.visualContainerObjects.title=[{properties:{show:literal(true),text:literal(title)}}];return v;}
export function slicer(seed,entity,property,title,x,y,width,height,z,options={}){
  const v=base(seed,'slicer',x,y,width,Math.max(height,76),z);
  v.visual.query={queryState:{Values:{projections:[column(entity,property,title)]}}};
  v.visual.objects={
    data:[{properties:{mode:literal('Dropdown')}}],
    header:[{properties:{show:literal(true),text:literal(title)}}],
  };
  if(options.singleSelect)v.visual.objects.selection=[{properties:{singleSelect:literal(true)}}];
  if(options.defaultValue!==undefined){
    v.visual.objects.general=[{properties:{filter:{filter:{
      Version:2,
      From:[{Name:'s',Entity:entity,Type:0}],
      Where:[{Condition:{In:{
        Expressions:[{Column:{Expression:{SourceRef:{Source:'s'}},Property:property}}],
        Values:[[{Literal:{Value:typeof options.defaultValue==='number'?`${options.defaultValue}L`:`'${String(options.defaultValue).replaceAll("'","''")}'`}}]],
      }}}],
    }}}}];
  }
  return v;
}
export function table(seed,fields,title,x,y,width,height,z){const v=base(seed,'tableEx',x,y,width,height,z);v.visual.query={queryState:{Values:{projections:fields}}};v.visual.visualContainerObjects.title=[{properties:{show:literal(true),text:literal(title)}}];v.visual.objects={total:[{properties:{totals:literal(false)}}],columnHeaders:[{properties:{autoSizeColumnWidth:literal(true)}}]};return v;}
export function chart(seed,type,category,values,title,x,y,width,height,z){const v=base(seed,type,x,y,width,height,z);v.visual.query={queryState:{Category:{projections:[category]},Y:{projections:values}}};v.visual.visualContainerObjects.title=[{properties:{show:literal(true),text:literal(title)}}];v.visual.drillFilterOtherVisuals=true;return v;}
