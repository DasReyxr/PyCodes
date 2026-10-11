import datetime
import pyperclip

LANGUAGES = {
    1: "Python", 2: "C", 3: "Arduino", 4: "Matlab", 5: "VHDL",
    6: "Javascript", 7: "R", 8: "ASM 8515", 9: "Latex", 10: "C 8515",
    11: "ASM ARM",12: "PIC ASM"
}

def main():
    language = get_language_choice()
    activity = input("\nIngresa el nombre de la actividad:\t")
    
    if language == 5:
        component_primal = input("Ingresa el nombre del componente:\t")
        pyperclip.copy(generate_code(language, activity, component_primal=component_primal))
        
        if get_yes_no("¿Deseas generar el Testbench?"):
            pyperclip.copy(generate_code(0, activity, component_primal))
        else:
            print("Operación finalizada.")
    else:
        pyperclip.copy(generate_code(language, activity))
    
    print("Código copiado al portapapeles.")

def get_language_choice():
    try:
        language = int(input("¿Qué lenguaje usas?\n1) Python\n2) C\n3) Arduino\n4) Matlab\n5) VHDL\n6) Javascript\n7) R\n8) Assembly \n9) Latex \n10) C 8515\n11) ARM ASM\n"))
        if language not in LANGUAGES:
            raise ValueError("Invalid choice")
        return language
    except ValueError as e:
        print(e)
        return get_language_choice()

def get_yes_no(prompt):
    try:
        return int(input(f"{prompt}\n1) Sí\n2) No\n")) == 1
    except ValueError:
        return get_yes_no(prompt)

def printing(stuff, sizet=26):
    size = len(stuff)
    aux = (sizet - size) // 2
    long = aux * '-'
    return f"{long} {stuff} {long}" if stuff else long * 2

def comment(argument):
    return {
        1: '"""',   # Python
        2: "/*",    # C Init
        3: "*/",    # C End
        4: "%{",    # Matlab Start
        5: "%}"     # Matlab End
    }.get(argument, "Invalid choice")

def commentline(argument):
    return {
        1: '#',     # Python / R
        2: "//",    # C / Arduino / Javascript
        3: "%",     # Matlab
        4: ";"      # Assembly
    }.get(argument, "Invalid choice")

def generate_code(opt, activity, component_primal="", num_out=1):
    current_date = datetime.date.today().strftime("%d/%m/%Y")
    name = "Orlando Reyes"
    name2 = "Auf Das"
    
    eh = ((name),(name2), (activity), (current_date))
    entire_header = f"{printing(name)}\n{printing(name2)}\n{printing(activity)}\n{printing(current_date)}\n"
    header_prime = ("Main Library", "Function")
    header = ("Class", "Variables", "Main")

    headerwc = ( "Variables", "Main")
    header_ml = ("Clear", "Variables", "Graph")
    header_r = (name, name2, activity, current_date)
    hd_embed = "Pin/out"
    body_arduino = "void setup(){\n\n}\nvoid loop(){\n\n}\n"
    
    code = ""
    match str(opt):
        case "1":  # Python
            code += generate_standard_code(1, entire_header, header_prime + header)
        case "2" | "6":  # C / Javascript
            code += generate_standard_code(2, entire_header, header_prime + header)
        case "4":  # Matlab
            code += generate_standard_code(4, entire_header, header_prime + header_ml)
            code += "clc;                                                % Clear the command window\nclear all;                                          % Clear all variables from the workspace\nhold off;\n"
        case "7":  # R
            code += generate_standard_code(1, eh, header_r + header_ml,inline=1)

        case "9": # Latex
            code += generate_standard_code(4, entire_header,inline=1)

        case "5":  # VHDL
            code += generate_vhdl_code(entire_header, component_primal)
        case "0":  # VHDL Testbench
            code += generate_testbench_code(entire_header, component_primal)
        
        #--- Microcontrolers ---
        case "3":  # Arduino
            code += generate_standard_code(2, entire_header, header + hd_embed) + f"\n{body_arduino}"
        case "8":  # Assembly 8515
            code += generate_assembly_code(entire_header, header_r + headerwc,1)
        case "10": # C 8515
            code += generate_standard_code(2, entire_header, header_prime + header)
        case "11":  # ARM ASM
            code += generate_assembly_code(entire_header, header_r + headerwc,2)
        case "12":  # ARM ASM
            code += generate_assembly_code(entire_header, header_r + headerwc,3)
       

    return code

def generate_standard_code(comment_type, entire_header, headers,inline =0):
    if inline == 0:
        code = f"{comment(comment_type)}\n{entire_header}{comment(comment_type+1)}\n"
        for hd in headers:
                code += f"{commentline(comment_type)} {printing(hd)}\n"
    else:
        code = ""
        for hd in headers:
            code += f"{commentline(comment_type)} {printing(hd)}\n"
    return code

def generate_vhdl_code(entire_header, component_primal):
    return (f"{printing('Code')}\n{entire_header}{printing('Main Library')}\n"
            f"library IEEE;\nuse IEEE.STD_LOGIC_1164.all;\n"
            f"{printing('Pin/out')}\n"
            f"entity {component_primal} is\n\tport\n\t\t(\n\t\t\t: in std_logic;\n\t\t\t: out std_logic\n\t\t);\n"
            f"end {component_primal};\n\n"
            f"architecture juve3dstudio of {component_primal} is\n\nbegin\nend juve3dstudio;")

def generate_assembly_code(entire_header, headers, val = 1):
    code =""
    for hd in headers:
        code += f"{commentline(4)} {printing(hd, 36)}\n"
    if val == 1:
        code += f'.include "M8515def.inc"\n'
        code += f'{commentline(4)} {printing("Interruptions Config")}\nRJMP SETCONFIG   ; Reset Handler  \nRJMP EXT_INT0   ; IRQ0 Handler  \nRJMP EXT_INT1   ; IRQ1 Handler  \nRJMP TIM1_CAPT   ; Timer1 Capture Handler  \nRJMP TIM1_COMPA   ; Timer1 CompareA Handler  \nRJMP TIM1_COMPB   ; Timer1 CompareB Handler  \nRJMP TIM1_OVF   ; Timer1 Overflow Handler  \nRJMP TIM0_OVF   ; Timer0 Overflow Handler  \nRJMP SPI_STC   ; SPI Transfer Complete Handler  \nRJMP USART_RXC   ; USART RX Complete Handler  \nRJMP USART_UDRE   ; UDR Empty Handler  \nRJMP USART_TXC   ; USART TX Complete Handler  \nRJMP ANA_COMP  ; Analog Comparator Handler  \nRJMP EXT_INT2  ; IRQ2 Handler    (no AT90S8515)  \nRJMP TIM0_COMP  ; Timer0 Compare Handler  (no AT90S8515)  \nRJMP EE_RDY   ; EEPROM Ready Handler  (no AT90S8515)  \nRJMP SPM_RDY   ; Store Program Memory Ready Handler(no AT90S8515) '
        code += f'\n\n{commentline(4)} {printing("Configuration")}\nSETCONFIG:\n\tLDI R16,high(RAMEND)\n\tOUT SPH,R16   ; Set Stack Pointer to top of RAM\n\tLDI R16,low(RAMEND) ; Parte baja\n\tOUT SPL,R16  ; Inicializar la pila\n\tCLI    ; Disable interrupts '
        code += f'\n\n{commentline(4)} {printing("Init")}\nINIT: \n\n\t RJMP INIT'
        code += f'\n\n{commentline(4)}{printing("Subrutines", 36)} \n\nBOTONES:\n\tret\n\n\n{commentline(4)} {printing("Interrupciones")} \nEXT_INT0:  RETI    ; IRQ0 Handler \nEXT_INT1:  RETI    ; IRQ1 Handler \nTIM1_CAPT:  RETI    ; Timer1 Capture Handler \nTIM1_COMPA: RETI    ; Timer1 CompareA Handler \nTIM1_COMPB: RETI    ; Timer1 CompareB Handler \nTIM1_OVF:  RETI    ; Timer1 Overflow Handler \nTIM0_OVF:  RETI    ; Timer0 Overflow Handler \nSPI_STC:  RETI    ; SPI Transfer Complete Handler \nUSART_RXC:  RETI    ; USART RX Complete Handler \nUSART_UDRE: RETI    ; UDR Empty Handler \nUSART_TXC:  RETI    ; USART TX Complete Handler \nANA_COMP:  RETI    ; Analog Comparator Handler \nEXT_INT2:  RETI    ; IRQ2 Handler \nTIM0_COMP:  RETI    ; Timer0 Compare Handler \nEE_RDY:  RETI    ; EEPROM Ready Handler \nSPM_RDY:  RETI    ; Store Program Memory Ready Handler'
    if val == 2:
        code += f"\tAREA juve3dstudio,CODE,READONLY\n\tENTRY\n\tEXPORT main\n\nmain\nciclo:\nB ciclo\nend\n"
    else:
        code += f""
    return code

def generate_testbench_code(entire_header, component_primal):
    return (f"{printing('Testbench')}\n{entire_header}"
            f"library IEEE;\nuse IEEE.STD_LOGIC_1164.all;\n"
            f"\nentity tb is\nend tb;\n\n"
            f"architecture sim of tb is\n\ncomponent {component_primal}\n\tport \n\t(\n\t : in std_logic;\n\t : out std_logic\n\t);\n"
            f"end component;\n\nsignal  : std_logic;\n\n"
            f"begin\n\tuut: {component_primal} port map ();\n\n\tprocess\n\tbegin\n"
            f"\t\twait for 1 us;\n\n\t\twait;\n\tend process;\n\nend sim;")

if __name__ == "__main__":
    main()