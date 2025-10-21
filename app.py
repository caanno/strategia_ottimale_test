import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(layout="wide", page_title="Strategia ottimale nei test a scelta multipla con penalità")


# --- CSS Personalizzato per Centratura e Stile Bottoni/Slider ---
# NOTA: Streamlit non ha un widget "bottone" nel body principale in questo caso, 
# ma i cambiamenti si applicano ai bottoni di interazione come quelli della sidebar o run/rerun.
st.markdown("""
<style>
/* Centra il titolo principale (un po' un hack, ma funziona) */
.css-1y5082y { /* Selector specifico per il block-container del titolo */
    text-align: center;
}
h1 {
    text-align: center;
    color: #4A90E2; /* Blu più acceso per il titolo */
}

/* Stilizzazione generica dei bottoni (widget buttons) */
.stButton>button {
    background-color: #4A90E2; /* Colore di sfondo blu */
    color: white; /* Testo bianco */
    padding: 10px 20px;
    border-radius: 12px; /* Bordi più arrotondati */
    border: none;
    box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3); /* Ombreggiatura */
    transition: all 0.2s ease-in-out;
}

.stButton>button:hover {
    background-color: #357ABD; /* Colore più scuro al passaggio del mouse */
    box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.4); 
    transform: translateY(-2px); /* Effetto leggero sollevamento */
}

/* Centratura degli header (h2/h3) */
h2, h3 {
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNZIONI DI CALCOLO
# ==============================================================================

@st.cache_data # Memorizza i risultati per prestazioni migliori
def calculate_E_j(k, p, q):
    """Calcola E_j (Valore Atteso Condizionato) e j_min."""
    E_j = []
    for j in range(k):
        if k - j == 0:
            Ej = p # Caso teorico: 1 opzione rimasta, si indovina sempre (j=k-1)
        else:
            prob_indovinare = 1 / (k - j)
            prob_sbagliare = (k - j - 1) / (k - j)
            Ej = prob_indovinare * p + prob_sbagliare * q
        E_j.append(Ej)
    
    # Trova il numero minimo di esclusioni per cui conviene rispondere (Ej > 0)
    j_min = next((j for j, Ej in enumerate(E_j) if Ej > 0), k)
    
    return E_j, j_min




# ==============================================================================
# INTERFACCIA STREAMLIT
# ==============================================================================


st.title("Strategia ottimale nei test a scelta multipla con penalità")
st.markdown("Questa applicazione mostra la strategia migliore in un test a scelta multipla con penalità. Calcola il valore atteso e scopri il numero minimo di opzioni che devi essere in grado di escludere con certezza per rendere la tua risposta casuale una scelta vantaggiosa, trasformando il rischio in un'opportunità di ottenere punti.")

# -----------------
# 1. INPUT
# -----------------
st.subheader("Inserisci i parametri del test")
col1,col2,col3=st.columns([1,2,1])
with col2:
    k = st.slider("Numero di opzioni per domanda ($k$)", 2, 10, 4)

col_input1, col_input2 = st.columns(2)
with col_input1:
    p = st.number_input("Punteggio risposta corretta ($p$)", 0.1, 10.0, 1.0, step=0.05)
with col_input2:
    q = st.number_input("Penalità risposta errata ($q$)", -10.0, 0.0, -0.5, step=0.05)
    
    # Controlla la condizione di penalita' (q deve essere minore di p/(k-1)) per avere E0 < 0
    if q >= p / (k - 1) and k > 1:
        st.warning(f"Attenzione! Con $q \\ge p/(k-1)$ (cioè $q \\ge {p/(k-1):.3f}$), il rischio scompare. La strategia 'Rispondi sempre' è sempre ottimale.")

x=False
col_left_btn, col_center_btn, col_right_btn = st.columns([4.75, 3, 3.5]) 
with col_center_btn:
    if st.button("Trova la strategia ottimale"):
        x=True

if x:
    
    # Esegui i calcoli principali
    E_j_list, j_min = calculate_E_j(k, p, q)
    # -----------------
    # 2. RISULTATI PRATICI E SOGLIE
    # -----------------
    st.divider()
    if E_j_list[0] == 0:
        st.info("Il valore atteso è 0: in questo situazione dare una risposta casuale  o non rispondere è statisticamente indifferente.")
        st.markdown("Nota: se devi minimizzare la possibilità di un punteggio negativo (o di un risultato molto basso), l'opzione di non rispondere è la scelta più cauta perché azzera la variabilità e il rischio di perdere punti.")
    elif E_j_list[0]>0:
        st.success("Rispondi sempre, non lasciare nessuna domanda in bianco!")
        st.markdown("La penalità è troppo bassa pertanto il valore atteso è positivo: anche se non sai nulla conviene dare una risposta casuale.")
    elif E_j_list[0]<0:
        st.error("Il valore atteso è negativo. Se non sai niente meglio lasciare in bianco!")
        st.markdown(f"Per ottenere un valore atteso positivo con una risposta casuale devi essere in grado di escludere con certezza **almeno {j_min} risposte su {k}**.")
    st.divider()
    st.subheader("Tabella decisionale")
    st.markdown("In base a quante opzioni di risposta riesci ad escludere con certezza, consulta questa tabella per vedere quale decisione prendere ad ogni domanda.")
    
    col_11,col_22 = st.columns([1,1])
    
    # Mostra la tabella E_j
    with col_11:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.dataframe(
            {
                "Opzioni escluse": list(range(k)),
                "Opzioni rimanenti": [k-j for j in range(k)],
                "Valore Atteso": [f"{ej:.3f}" for ej in E_j_list],
                "Decisione": ["Rispondi" if ej > 0 else "Non rispondere" for ej in E_j_list]
            },
            hide_index=True
        )

    # -----------------
    # 4. GRAFICO VISUALE
    # -----------------
    #col_empty_left, col_chart, col_empty_right = st.columns([1.5, 2, 1.5])
    with col_22:
        fig, ax = plt.subplots(figsize=(6, 3))
        x = np.arange(k)
        y = np.array(E_j_list)
        # Colori per indicare la decisione
        colors = ['green' if val > 0 else 'red' for val in y]
        ax.bar(x, y, color=colors, alpha=0.7)
        # Linea E[X]=0
        ax.axhline(0, color='black', linestyle='--', linewidth=1)
        ax.set_title(f"Visualizzazione del punteggio atteso in base alle esclusioni ($j$)", fontsize=10)
        ax.set_xlabel("Numero di risposte errate escluse ($j$)", fontsize=8)
        ax.set_ylabel("Punteggio atteso $E_j$", fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"j={i}" for i in range(k)])
        ax.set_yticks(np.arange(0,p+0.01,0.25))
        ax.set_yticklabels(np.arange(0,p+0.01,0.25))    
        ax.grid(axis='y', linestyle='dotted', alpha=0.6)
        st.pyplot(fig)
    st.markdown("---")
    st.markdown("""
    #### 📘 Approfondimento
    Questo progetto è descritto nel documento *“Modellazione probabilistica e strategia ottimale nei test a scelta multipla”*, che illustra i modelli alla base di questa applicazione.<br>Per leggere il documento clicca qui.
    """, unsafe_allow_html=True)