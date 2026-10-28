let
 Dates=List.Dates(#date(2025,1,1),730,#duration(1,0,0,0)),
 T=Table.FromList(Dates,Splitter.SplitByNothing(),{"Date"}),
 Typed=Table.TransformColumnTypes(T,{{"Date",type date}}),
 Year=Table.AddColumn(Typed,"Year",each Date.Year([Date]),Int64.Type),
 Month=Table.AddColumn(Year,"YearMonth",each Date.ToText([Date],"yyyy-MM"),type text)
in Month