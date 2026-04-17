import os
import re

def count_words_in_latex(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rimuove i commenti LaTeX (% ...)
    content = re.sub(r'%.*', '', content)
    
    # Rimuove i comandi LaTeX (\comando{...} o \comando)
    # Questa regex cerca di mantenere il testo dentro le graffe per comandi comuni come \section{Testo}
    content = re.sub(r'\\[a-zA-Z]+\*?\{([\s\S]*?)\}', r'\1', content)
    content = re.sub(r'\\[a-zA-Z]+\*?', '', content)
    
    # Rimuove simboli speciali e punteggiatura extra per il conteggio
    words = re.findall(r'\b\w+\b', content)
    return len(words)

def main():
    inc_dir = 'inc'
    total_words = 0
    
    if not os.path.exists(inc_dir):
        print(f"Errore: La cartella '{inc_dir}' non esiste.")
        return

    print(f"{'File':<30} | {'Parole':<10}")
    print("-" * 45)

    # Lista i file e conta le parole
    for filename in sorted(os.listdir(inc_dir)):
        if filename.endswith('.tex'):
            path = os.path.join(inc_dir, filename)
            count = count_words_in_latex(path)
            total_words += count
            print(f"{filename:<30} | {count:<10}")

    print("-" * 45)
    print(f"{'TOTALE PAROLE':<30} | {total_words:<10}")

if __name__ == "__main__":
    main()
