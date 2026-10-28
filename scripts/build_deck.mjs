import fs from 'node:fs/promises';
import path from 'node:path';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
import {pathToFileURL} from 'node:url';
const root=process.env.PROJECT_ROOT || path.resolve('wealthsimple-marketing');
const r=JSON.parse(await fs.readFile(path.join(root,'data/analysis/findings.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
const C={navy:'#17324D',teal:'#007F78',muted:'#64748B',light:'#EDF3F6',amber:'#A45F14'};
const font='Arial';
function text(s,v,x,y,w,h,size=24,color=C.navy,bold=false){let o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{style:'solid',fill:'none',width:0}});o.text=v;o.text.style={typeface:font,fontSize:size,color,bold};return o;}
function slide(title,sub){const s=p.slides.add();s.background.fill='#FFFFFF';text(s,title,60,40,1160,92,40,C.navy,true);if(sub)text(s,sub,60,135,1160,58,21,C.muted);text(s,`${p.slides.items.length}   Fictional training case • CAD`,60,674,1140,24,13,C.muted);s.speakerNotes.text='Source: supplied Power_BI_project.xlsx, reviewed data/analysis/findings.json and population_sensitivity.csv. Comparable population: 1,671 complete, sequential funnel records with usable marketing cost. Counts are recorded customers, not deduplicated people. All findings are descriptive.';return s;}
function table(s,vals,x=60,y=220,w=1160,h=350,widths){const t=s.tables.add({rows:vals.length,columns:vals[0].length,left:x,top:y,width:w,height:h,values:vals,columnWidths:widths});t.borders.assign({style:'solid',fill:'#D7E0E7',width:.6});for(let i=0;i<vals.length;i++)for(let j=0;j<vals[0].length;j++){let c=t.getCell(i,j);c.fill=i===0?C.navy:i%2===0?C.light:'#FFFFFF';c.text.style={typeface:font,fontSize:21,color:i===0?'#FFFFFF':C.navy,bold:i===0};}return t;}
function chart(s,cats,vals,{x=60,y=220,w=760,h=380,format='#,##0',label='Recorded paying customers',color=C.teal}={}){return s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},categories:cats,series:[{name:label,values:vals.map(v=>Number(v.toPrecision(12))),fill:color}],barOptions:{direction:'bar',grouping:'clustered',gapWidth:70},hasLegend:false,xAxis:{textStyle:{typeface:font,fontSize:19,fill:C.navy}},yAxis:{min:0,numberFormatCode:format,textStyle:{typeface:font,fontSize:17,fill:C.muted},majorGridlines:{style:'solid',fill:'#E3EAF0',width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:format,textStyle:{typeface:font,fontSize:18,fill:C.navy}},chartFill:'#FFFFFF'});}
let s=slide('Marketing efficiency and\ncustomer conversion','Wealthsimple Canada training case');
text(s,'A decision framework for acquisition tests\nand better marketing measurement',60,260,1100,120,34,C.teal,true);
text(s,'Emmanuel F. Kebodi\n28 October 2026',60,468,800,80,24);
text(s,'Scenario data for 2025–2026. No claim of actual company performance.',60,596,1150,45,20,C.muted);
s=slide('High acquisition cost in the comparable population','Headline metrics use the same eligible records for costs and customer counts.');
table(s,[['Measure','Result'],['Eligible campaign records','1,671 of 2,000'],['Marketing cost','CAD 426,714'],['Recorded paying customers','106'],['Signup-to-paying conversion','0.77%'],['Blended CAC','CAD 4,026']],60,210,735,390,[480,255]);
text(s,'329 records excluded\nfrom comparison',850,242,350,110,32,C.amber,true);text(s,'CAD 82,177 of known cost remains visible in the audit population. Six source records still lack a cost value.',850,380,350,170,24);
s=slide('Validation changes the customer total','Three source rows each claim 100 paying customers with zero funded accounts.');
chart(s,['Unvalidated numeric counts','Consistent funnel','Funnel and usable cost','Also requires trusted date'],[607,108,106,96],{w:790});
text(s,'All 2,000 rows retained',900,230,300,75,28,C.teal,true);text(s,'No absolute-value repair of negatives.\n\nMissing values remain distinct from zero.\n\nCohort sequence is an explicit assumption.',900,330,300,260,23);
s=slide('Paid Search records 69 of 106 paying customers','Email and Referral show lower observed CAC, with only 9 and 13 customers.');
chart(s,['Paid Search','Referral','Organic Search','Email','Affiliate'],[69,13,9,9,6],{w:760});
text(s,'CAC by channel',885,220,320,55,28,C.teal,true);text(s,'Paid Search     CAD 882\nReferral           CAD 346\nOrganic Search CAD 749\nEmail               CAD 327\nAffiliate         CAD 2,433',885,295,340,230,23);
text(s,'Six channels have zero recorded paying customers. Their CAC is undefined.',885,545,330,100,21,C.muted);
s=slide('0.77% of signups become recorded paying customers','4.56m impressions / 136,235 clicks / 13,700 signups / 1,673 funded / 106 paying');
chart(s,['Impressions to clicks','Clicks to signups','Signups to funded','Funded to paying'],[r.totals.ctr,r.totals.click_signup,r.totals.signup_funded,r.totals.funded_paying],{w:780,format:'0.00%',label:'Step conversion'});
text(s,'12,027',900,240,300,65,46,C.teal,true);text(s,'signups do not reach funding',900,310,300,80,24);
text(s,'1,567',900,420,300,65,46,C.teal,true);text(s,'funded accounts do not reach payment',900,490,300,85,24);
s=slide('Campaign families for review and controlled tests','Zero recorded output is a review signal. It does not establish wasted spend.');
table(s,[['Campaign family','Cost CAD','Paying','Next step'],['Investing Explained Pre-roll','25,150','0','Review objective and lag'],['Retargeting Carousel','24,491','0','Review tracking and creative'],['Finance News Display','23,093','0','Review attribution'],['Trade Account Search','17,025','36','Capped acquisition test'],['Dormant Lead Nurture','1,408','7','Small lifecycle test']],60,210,1160,340,[430,160,110,460]);
text(s,'19 zero-output families account for CAD 337,080, or 79.0% of eligible cost. No automatic pause or scaling rule is justified.',60,585,1160,65,23,C.muted);
s=slide('Audience differences need validation before scaling','Small customer counts and channel mix limit conclusions about segments, regions and devices.');
table(s,[['Comparison','Paying customers','Observed CAC CAD'],['First-time Investors / Parents','19 / 5','2,685 / 10,999'],['Quebec / Ontario','17 / 6','2,655 / 6,869'],['Desktop / iOS','30 / 15','2,866 / 5,405'],['Mortgage product focus','3','20,919']],60,220,1160,300,[560,290,310]);
text(s,'Use product-specific observation windows and matched comparisons. Aggregate rankings do not prove targeting quality or causal effects.',60,565,1140,80,25,C.teal,true);
s=slide('First-month returns do not establish lifetime profit','Known revenue is CAD 4,689 on 1,646 eligible records with a usable revenue value.');
table(s,[['Measure on matched records','Result'],['Revenue / ad spend','0.0135x'],['Revenue / total marketing cost','0.0112x'],['Revenue less total marketing cost','CAD −414,869'],['Average revenue per recorded paying customer','CAD 44.66']],60,220,1160,290,[850,310]);
text(s,'1,886 source rows report zero revenue; 33 are missing or invalid. Zero is not proof of failed attribution. Margin, later revenue and retention are unavailable.',60,550,1140,100,24,C.muted);
s=slide('Seven Power BI views support the review','Shared channel, campaign, period, province, segment, device and product filters.');
table(s,[['Dashboard page','Decision supported'],['Data Quality','Which records and fields need correction?'],['Spend and CAC','Where is cost concentrated?'],['Conversion Funnel','Which funnel transitions need testing?'],['Channel and Campaign','Which comparisons justify further investigation?'],['Revenue and ROAS','What does first-month revenue cover?'],['Audience and Region','How do product, device and audience results differ?'],['Budget Optimization','Which hypotheses should receive a capped test?']],60,205,1160,400,[430,730]);
s=slide('Measurement repair precedes budget expansion','Suggested sequence and accountable teams. Timing starts when the project is adopted.');
table(s,[['When','Owner','Action and success measure'],['Weeks 1–2','Analytics','Resolve anomalies and identity collisions; track exclusions'],['Weeks 2–4','Growth','Capped channel tests; incremental customers and CAC'],['Weeks 2–4','Product and lifecycle','Funding and activation tests; stage conversion rates'],['Monthly','Finance and marketing','Set payback-based CAC limits; review matched returns']],60,220,1160,330,[180,270,710]);
text(s,'No guaranteed revenue uplift or CAC saving is claimed. Approve test budgets and success criteria before moving spend.',60,585,1160,65,25,C.teal,true);
const stage=path.resolve('build/deck-review');await fs.mkdir(stage,{recursive:true});
for(let i=0;i<p.slides.items.length;i++){let b=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(stage,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const candidate=path.join(stage,'candidate.pptx');await(await PresentationFile.exportPptx(p)).save(candidate);
const skill='/root/.codex/skills/builtins/presentations';const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
await finalizePresentation({workspaceDir:path.resolve('.'),candidatePath:candidate,finalPath:path.join(root,'reports/Wealthsimple_Executive_Deck.pptx'),pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...[2,6,7,8,9,10].flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:10,requiredNativeChartOwnerSlides:[3,4,5],requiredNativeTableOwnerSlides:[2,6,7,8,9,10],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(stage,'validation.json')});
console.log('Deck completed');
