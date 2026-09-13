import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {column,measure,text,card,slicer,table,chart} from './visuales.mjs';

const root=path.resolve(process.argv[2]||'.');
const report=path.join(root,'Retencion_Academica_SIES.Report');
const model=path.join(root,'Retencion_Academica_SIES.SemanticModel');
const data=path.join(root,'datos');
const runtimeDataPath=path.resolve(process.env.PBIP_DATA_PATH||data).replaceAll('"','""');
const metadata=JSON.parse(fs.readFileSync(path.join(data,'metadata.json'),'utf8'));
const write=(file,value)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,typeof value==='string'?value:JSON.stringify(value,null,2)+'\n','utf8');};
const hash=seed=>crypto.createHash('sha256').update(seed).digest('hex').slice(0,20);
const guid=seed=>{const h=crypto.createHash('sha256').update(seed).digest('hex');return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20,32)}`;};
const q=value=>`'${String(value).replaceAll("'","''")}'`;

for(const file of fs.readdirSync(path.join(model,'definition','tables')))fs.rmSync(path.join(model,'definition','tables',file));
for(const file of fs.readdirSync(path.join(report,'definition','pages')))fs.rmSync(path.join(report,'definition','pages',file),{recursive:true,force:true});

write(path.join(model,'definition','database.tmdl'),'database\n\tcompatibilityLevel: 1606\n');
write(path.join(model,'definition','expressions.tmdl'),`expression 'Ruta datos' = "${runtimeDataPath}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n`);
write(path.join(model,'definition','model.tmdl'),`model Model
\tculture: es-CL
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: es-CL

annotation PBI_ProTooling = ["DevMode"]

ref table Seguimiento
ref table Programas
ref table Cohortes
ref table Horizontes

ref cultureInfo es-CL
`);
write(path.join(model,'definition','cultures','es-CL.tmdl'),'cultureInfo es-CL\n');

const scoped=expression=>`VAR _contextoValido=HASONEVALUE('Cohortes'[Cohorte]) && HASONEVALUE('Horizontes'[AnioDesdeIngreso])\nRETURN IF(_contextoValido,${expression})`;
const measures=[
 ['N Base',scoped("DISTINCTCOUNT('Seguimiento'[TrayectoriaID])"),'#,##0'],
 ['N Carrera',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[TrayectoriaID]),'Seguimiento'[EnCarrera]=1)"),'#,##0'],
 ['N Institucion',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[TrayectoriaID]),'Seguimiento'[EnInstitucion]=1)"),'#,##0'],
 ['N Educacion Superior',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[TrayectoriaID]),'Seguimiento'[EnEducacionSuperior]=1)"),'#,##0'],
 ['Tasa Carrera','DIVIDE([N Carrera],[N Base])','0.0%'],
 ['Tasa Institucion','DIVIDE([N Institucion],[N Base])','0.0%'],
 ['Tasa Educacion Superior','DIVIDE([N Educacion Superior],[N Base])','0.0%'],
 ['Personas',scoped("DISTINCTCOUNT('Seguimiento'[MRUN])"),'#,##0'],
 ['Personas Institucion',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[MRUN]),'Seguimiento'[EnInstitucion]=1)"),'#,##0'],
 ['Personas Educacion Superior',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[MRUN]),'Seguimiento'[EnEducacionSuperior]=1)"),'#,##0'],
 ['Tasa Institucion Personas','DIVIDE([Personas Institucion],[Personas])','0.0%'],
 ['Tasa Educacion Superior Personas','DIVIDE([Personas Educacion Superior],[Personas])','0.0%'],
 ['N Titulados',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[TrayectoriaID]),'Seguimiento'[TituladoAcumulado]=1)"),'#,##0'],
 ['Tasa Titulacion','DIVIDE([N Titulados],[N Base])','0.0%'],
 ['N Movilidad ECS',scoped("CALCULATE(DISTINCTCOUNT('Seguimiento'[TrayectoriaID]),'Seguimiento'[MovilidadInternaECS]=1)"),'#,##0'],
 ['ECS Base',"CALCULATE([N Base],KEEPFILTERS('Programas'[GrupoECS]=\"ECS\"))",'#,##0'],
 ['ECS Tasa Carrera',"CALCULATE([Tasa Carrera],KEEPFILTERS('Programas'[GrupoECS]=\"ECS\"))",'0.0%'],
 ['ECS Tasa Institucion',"CALCULATE([Tasa Institucion],KEEPFILTERS('Programas'[GrupoECS]=\"ECS\"))",'0.0%'],
 ['ECS Tasa Educacion Superior',"CALCULATE([Tasa Educacion Superior],KEEPFILTERS('Programas'[GrupoECS]=\"ECS\"))",'0.0%'],
 ['Estado seleccion',`SWITCH(TRUE(),NOT HASONEVALUE('Cohortes'[Cohorte]),"Seleccione exactamente una cohorte",NOT HASONEVALUE('Horizontes'[AnioDesdeIngreso]),"Seleccione exactamente un seguimiento","OK")`,'@'],
 ['Definicion MRUN','"MRUN es el identificador enmascarado publicado por SIES; no corresponde al RUT real."','@'],
];
let fact='table Seguimiento\n\n';
for(const [name,dax,format] of measures)fact+=`\tmeasure ${q(name)} =\n${dax.split('\n').map(line=>'\t\t\t'+line).join('\n')}\n\t\tformatString: ${format}\n\t\tdisplayFolder: Indicadores reproducibles\n\n`;
const factCols={MRUN:'string',TrayectoriaID:'string',ProgramaID:'string',Cohorte:'int64',AnioObservado:'int64',AnioDesdeIngreso:'int64',Observable:'int64',EnCarrera:'int64',EnInstitucion:'int64',EnEducacionSuperior:'int64',EnECS:'int64',MovilidadInternaECS:'int64',TituladoAcumulado:'int64'};
for(const [name,type] of Object.entries(factCols))fact+=`\tcolumn ${q(name)}\n\t\tdataType: ${type}\n\t\tsummarizeBy: none\n\t\tsourceColumn: ${name}\n${['MRUN','TrayectoriaID','ProgramaID'].includes(name)?'\t\tisHidden\n':''}\n`;
const factTypes=Object.entries(factCols).map(([name,type])=>`{"${name}",${type==='string'?'type text':'Int64.Type'}}`).join(',');
fact+=`\tpartition Seguimiento = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tFiles = Folder.Files(#"Ruta datos"),
\t\t\t\tSelected = Table.SelectRows(Files, each Text.StartsWith([Name], "seguimiento_") and Text.EndsWith([Name], ".csv.gz")),
\t\t\t\tParsed = Table.AddColumn(Selected, "Rows", each Table.PromoteHeaders(Csv.Document(Binary.Decompress([Content], Compression.GZip), [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true])),
\t\t\t\tCombined = Table.Combine(Parsed[Rows]),
\t\t\t\tTypes = Table.TransformColumnTypes(Combined,{${factTypes}},"en-US")
\t\t\tin Types
`;
write(path.join(model,'definition','tables','Seguimiento.tmdl'),fact);

function csvTable(name,file,columns){let out=`table ${name}\n\n`;for(const [col,type] of Object.entries(columns))out+=`\tcolumn ${q(col)}\n\t\tdataType: ${type}\n\t\tsummarizeBy: none\n\t\tsourceColumn: ${col}\n${col.endsWith('ID')?'\t\tisHidden\n':''}\n`;const types=Object.entries(columns).map(([col,type])=>`{"${col}",${type==='string'?'type text':'Int64.Type'}}`).join(',');out+=`\tpartition ${name} = m
\t\tmode: import
\t\tsource =
\t\t\tlet
\t\t\t\tSource = Csv.Document(File.Contents(#"Ruta datos" & "/${file}"), [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\tTypes = Table.TransformColumnTypes(Headers,{${types}},"en-US")
\t\t\tin Types
`;return out;}
write(path.join(model,'definition','tables','Programas.tmdl'),csvTable('Programas','programas.csv',{ProgramaID:'string',Cohorte:'int64',InstitucionID:'string',Institucion:'string',TipoInstitucion:'string',CodigoCarrera:'string',Carrera:'string',Nivel:'string',Area:'string',ModalidadOrigen:'string',JornadaOrigen:'string',AmbitoFlexible:'string',GrupoECS:'string',RegistrosOrigen:'int64'}));
write(path.join(model,'definition','tables','Cohortes.tmdl'),csvTable('Cohortes','cohortes.csv',{Cohorte:'int64'}));
write(path.join(model,'definition','tables','Horizontes.tmdl'),csvTable('Horizontes','horizontes.csv',{AnioDesdeIngreso:'int64',Etiqueta:'string'}));
write(path.join(model,'definition','relationships.tmdl'),`relationship ${guid('programa')}\n\tfromColumn: Seguimiento.ProgramaID\n\ttoColumn: Programas.ProgramaID\n\nrelationship ${guid('cohorte')}\n\tfromColumn: Seguimiento.Cohorte\n\ttoColumn: Cohortes.Cohorte\n\nrelationship ${guid('horizonte')}\n\tfromColumn: Seguimiento.AnioDesdeIngreso\n\ttoColumn: Horizontes.AnioDesdeIngreso\n`);

write(path.join(model,'.platform'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json',metadata:{type:'SemanticModel',displayName:'Retención Académica SIES'},config:{version:'2.0',logicalId:guid('semantic-model')}});
write(path.join(report,'.platform'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json',metadata:{type:'Report',displayName:'Retención Académica SIES'},config:{version:'2.0',logicalId:guid('report')}});
write(path.join(report,'definition.pbir'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json',version:'4.0',datasetReference:{byPath:{path:'../Retencion_Academica_SIES.SemanticModel'}}});
write(path.join(report,'definition','report.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json',themeCollection:{},settings:{useStylableVisualContainerHeader:true,useEnhancedTooltips:false}});

const pages=[
 ['Resumen nacional','Indicadores IP+CFT para trayectorias no presenciales, semipresenciales o con jornada a distancia.'],
 ['Cohortes','Evolución de las tres tasas con denominadores recalculados por cohorte y seguimiento.'],
 ['Instituciones','Comparación descriptiva; no es un ranking ajustado por composición.'],
 ['Modalidad y jornada','Composición y resultados según el formato declarado en la matrícula de origen.'],
 ['ECS','Vista dedicada al IP Escuela de Comercio de Santiago (171) y CFT Escuela de Comercio (426).'],
 ['Titulación','Titulación registrada hasta 2024 para las trayectorias analizadas.'],
 ['Metodología','Definiciones, unidad de análisis, fuentes y condiciones de reproducibilidad.'],
].map(([label,subtitle],i)=>({label,subtitle,id:hash(`page-${i}-${label}`)}));
const filters=(seed,{cohortDefault=true}={})=>[
 slicer(`slicer-${seed}-cohorte`,'Cohortes','Cohorte','Cohorte',32,142,250,72,10,{singleSelect:true,...(cohortDefault?{defaultValue:2024}:{})}),
 slicer(`slicer-${seed}-horizonte`,'Horizontes','AnioDesdeIngreso','Seguimiento',298,142,250,72,11,{singleSelect:true,defaultValue:2}),
 slicer(`slicer-${seed}-tipo`,'Programas','TipoInstitucion','Tipo de institución',564,142,310,72,12),
 slicer(`slicer-${seed}-ambito`,'Programas','AmbitoFlexible','Ámbito flexible',890,142,360,72,13),
];
const header=(page,i)=>[text(`title-${i}`,page.label,32,24,1536,56,0,'28px','#173277','700'),text(`sub-${i}`,page.subtitle,32,82,1536,40,1,'14px','#4B5563','400')];
const body=[];
body[0]=[...filters('r'),card('r-base','Seguimiento','N Base','Trayectorias',32,248,360,112,20),card('r-c','Seguimiento','Tasa Carrera','Retención académica',408,248,360,112,21),card('r-i','Seguimiento','Tasa Institucion','Retención institucional',784,248,360,112,22),card('r-e','Seguimiento','Tasa Educacion Superior','Retención en educación superior',1160,248,408,112,23),table('r-personas',[measure('Seguimiento','Personas','Personas MRUN'),measure('Seguimiento','Tasa Institucion Personas','Retención institucional'),measure('Seguimiento','Tasa Educacion Superior Personas','Retención en ES')],'Lectura complementaria por personas distintas',32,392,744,220,24),chart('r-trend','lineChart',column('Cohortes','Cohorte','Cohorte'),[measure('Seguimiento','Tasa Carrera','Académica'),measure('Seguimiento','Tasa Institucion','Institucional'),measure('Seguimiento','Tasa Educacion Superior','Educación superior')],'Evolución por cohorte',792,392,776,360,25),text('r-note','Seleccione exactamente una cohorte y un seguimiento para los KPI. Las tendencias usan el contexto de cada punto; no se promedian porcentajes.',32,650,744,80,26,'15px','#374151','400')];
body[1]=[...filters('c',{cohortDefault:false}),chart('c-trend','lineChart',column('Cohortes','Cohorte','Cohorte'),[measure('Seguimiento','Tasa Carrera','Académica'),measure('Seguimiento','Tasa Institucion','Institucional'),measure('Seguimiento','Tasa Educacion Superior','Educación superior')],'Tres indicadores por cohorte',32,248,1000,500,20),table('c-table',[column('Cohortes','Cohorte','Cohorte'),measure('Seguimiento','N Base','Base'),measure('Seguimiento','Tasa Carrera','Académica'),measure('Seguimiento','Tasa Institucion','Institucional'),measure('Seguimiento','Tasa Educacion Superior','Educación superior')],'Valores exactos',1048,248,520,500,21)];
body[2]=[...filters('i'),table('i-table',[column('Programas','Institucion','Institución'),column('Programas','TipoInstitucion','Tipo'),measure('Seguimiento','N Base','Base'),measure('Seguimiento','Tasa Carrera','Académica'),measure('Seguimiento','Tasa Institucion','Institucional'),measure('Seguimiento','Tasa Educacion Superior','Educación superior')],'Resultados por institución de origen',32,248,1536,500,20),text('i-note','Una persona puede originar más de una trayectoria. Para comparaciones institucionales revise conjuntamente base, cohorte, modalidad y jornada.',32,776,1536,60,21,'15px','#374151','400')];
body[3]=[...filters('m'),chart('m-a','clusteredColumnChart',column('Programas','AmbitoFlexible','Ámbito'),[measure('Seguimiento','N Base','Trayectorias')],'Composición del universo flexible',32,248,744,280,20),chart('m-j','clusteredColumnChart',column('Programas','JornadaOrigen','Jornada'),[measure('Seguimiento','N Base','Trayectorias')],'Jornada declarada en origen',792,248,776,280,21),table('m-table',[column('Programas','AmbitoFlexible','Ámbito'),column('Programas','JornadaOrigen','Jornada'),measure('Seguimiento','N Base','Base'),measure('Seguimiento','Tasa Carrera','Académica'),measure('Seguimiento','Tasa Institucion','Institucional'),measure('Seguimiento','Tasa Educacion Superior','Educación superior')],'Indicadores recalculados por modalidad y jornada',32,552,1536,270,22)];
body[4]=[...filters('e'),card('e-base','Seguimiento','ECS Base','Trayectorias ECS',32,248,360,112,20),card('e-c','Seguimiento','ECS Tasa Carrera','Retención académica ECS',408,248,360,112,21),card('e-i','Seguimiento','ECS Tasa Institucion','Retención institucional ECS',784,248,360,112,22),card('e-s','Seguimiento','ECS Tasa Educacion Superior','Retención ES ECS',1160,248,408,112,23),table('e-table',[column('Programas','Institucion','Institución ECS'),measure('Seguimiento','ECS Base','Base'),measure('Seguimiento','ECS Tasa Carrera','Académica'),measure('Seguimiento','ECS Tasa Institucion','Institucional'),measure('Seguimiento','ECS Tasa Educacion Superior','Educación superior'),measure('Seguimiento','N Movilidad ECS','Movilidad IP↔CFT')],'IP 171 y CFT 426',32,392,1536,280,24),text('e-note','El cambio entre IP 171 y CFT 426 se informa como movilidad interna ECS; no se considera retención en la misma institución jurídica.',32,704,1536,70,25,'15px','#374151','400')];
body[5]=[...filters('t'),card('t-base','Seguimiento','N Base','Trayectorias',32,248,480,112,20),card('t-n','Seguimiento','N Titulados','Con titulación registrada',528,248,480,112,21),card('t-r','Seguimiento','Tasa Titulacion','Tasa acumulada',1024,248,544,112,22),table('t-table',[column('Cohortes','Cohorte','Cohorte'),measure('Seguimiento','N Base','Base'),measure('Seguimiento','N Titulados','Titulados'),measure('Seguimiento','Tasa Titulacion','Tasa')],'Titulación por cohorte',32,392,1536,330,23),text('t-note','La fuente de titulados cubre 2011–2024. La ausencia de un registro no permite inferir por sí sola deserción o retiro.',32,752,1536,60,24,'15px','#374151','400')];
body[6]=[text('met-1','UNIVERSO',32,158,480,36,10,'18px','#173277','700'),text('met-2','Pregrado en IP y CFT. Se incluye una trayectoria cuando la matrícula de origen es No Presencial, Semipresencial o tiene jornada A Distancia. La unión se deduplica.',32,202,480,150,11,'15px','#374151','400'),text('met-3','UNIDAD Y MRUN',544,158,480,36,12,'18px','#173277','700'),text('met-4','La unidad principal es MRUN–carrera–institución–cohorte. MRUN es la llave enmascarada publicada por SIES. No existe ni se usa un campo RUT.',544,202,480,150,13,'15px','#374151','400'),text('met-5','INDICADORES',1056,158,512,36,14,'18px','#173277','700'),text('met-6','Académica: misma carrera e institución. Institucional: misma institución jurídica. Educación superior: cualquier matrícula posterior en el sistema.',1056,202,512,150,15,'15px','#374151','400'),text('met-7','REPRODUCIBILIDAD',32,396,1536,36,16,'18px','#173277','700'),text('met-8','Los CSV seguimiento_*.csv.gz contienen MRUN, TrayectoriaID y los indicadores binarios. Las medidas DAX usan DISTINCTCOUNT; resultados_control.csv permite una conciliación independiente. Las bases oficiales completas no se incluyen por su tamaño: fuentes.json registra archivo, año y SHA-256.',32,444,1536,130,17,'15px','#374151','400'),text('met-9','FUENTES Y CORTE',32,614,1536,36,18,'18px','#173277','700'),text('met-10','Matrícula SIES 2011–2025 y titulados SIES 2011–2024. Reconstrucción propia sobre datos abiertos; no corresponde a un indicador oficial certificado por SIES.',32,662,1536,100,19,'15px','#374151','400')];

const visualNames=[];
for(let i=0;i<pages.length;i++)for(const visual of [...header(pages[i],i),...body[i]])visualNames.push(visual.name);
if(new Set(visualNames).size!==visualNames.length)throw new Error('Existen identificadores visuales duplicados');
if(visualNames.length!==73)throw new Error(`Se esperaban 73 visuales y se generaron ${visualNames.length}`);

for(let i=0;i<pages.length;i++){
 const page=pages[i],dir=path.join(report,'definition','pages',page.id);
 write(path.join(dir,'page.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',name:page.id,displayName:page.label,displayOption:'FitToPage',width:1600,height:900,objects:{background:[{properties:{color:{solid:{color:'#F4F6F8'}},transparency:{expr:{Literal:{Value:'0D'}}}}}]}});
 [...header(page,i),...body[i]].forEach((visual,index)=>{visual.position.tabOrder=index;visual.position.z=index;write(path.join(dir,'visuals',visual.name,'visual.json'),visual);});
}
write(path.join(report,'definition','pages','pages.json'),{$schema:'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json',pageOrder:pages.map(p=>p.id),activePageName:pages[0].id});
write(path.join(root,'pbip.manifest.json'),{name:'Retencion_Academica_SIES',version:metadata.version_metodologica,dataCutoff:'matrícula 2025 / titulados 2024',pages:pages.map(p=>({id:p.id,label:p.label})),sourceYears:{matricula:metadata.matricula_anios,titulados:metadata.titulados_anios}});
console.log(JSON.stringify({project:root,pages:pages.length,measures:measures.length},null,2));
