from llama_parse import LlamaParse
import os



class BankStatementParser:
    def __init__(self, api_key, result_type="markdown", premium_mode=False):
        self.parser = LlamaParse(result_type=result_type, 
                                api_key=api_key, 
                                premium_mode=premium_mode)
    
    
    
    def extract_tables_from_markdown(self, markdown_content):
        tables = []
        lines = markdown_content.split('\n')
        table = []
        in_table = False

        for line in lines:
            if line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    in_table = True
                table.append(line)
            else:
                if in_table:
                    tables.append('\n'.join(table))
                    table = []
                    in_table = False

        if in_table:
            tables.append('\n'.join(table))

        return tables
    
    def parse_statement(self, file, output_dir):
        documents = self.parser.load_data(file)
        tables = []
        for doc in documents:
            markdown_content = doc.text
            tables_extract = self.extract_tables_from_markdown(markdown_content)
            for table in tables_extract:
                tables.append(table)

        os.makedirs(output_dir, exist_ok=True)
        
        # Print the extracted tables
        for i, table in enumerate(tables):
            file_path = os.path.join(output_dir, f"table{i}.md")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(table)
        
        return tables
                
        
        