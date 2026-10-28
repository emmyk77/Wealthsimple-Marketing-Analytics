let
    Workbook = Excel.Workbook(File.Contents(DataRoot & "/data/raw/Power_BI_project.xlsx"), null, true),
    Sheet = Workbook{[Item="Sheet1",Kind="Sheet"]}[Data],
    Headers = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true])
in Headers