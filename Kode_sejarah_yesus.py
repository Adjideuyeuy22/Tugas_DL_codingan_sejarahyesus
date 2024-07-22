import os
import flet as ft
from dotenv import load_dotenv
import google.generativeai as genai
from bert_score import score

load_dotenv()

# Kunci API Google Gemini
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(
    api_key=api_key
)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Mengubah filter dan instruksi khusus untuk topik Yesus
def filter_yesus(response_text):
    # Fungsi untuk memfilter data hanya untuk topik Yesus
    lines = response_text.split('\n')
    yesus_responses = [line for line in lines if 'Yesus' in line]
    if not yesus_responses:
        return "Maaf, saya tidak memiliki informasi tentang topik ini."
    return '\n'.join(yesus_responses)

def compute_bertscore(hypothesis, reference):
    # Menghitung BERTScore antara hipotesis dan referensi
    P, R, F1 = score([hypothesis], [reference], lang='en', verbose=True)
    return P.item(), R.item(), F1.item()

def main(page: ft.Page):
    global isAsking  # Menambahkan global isAsking
    isAsking = False  # Menambahkan inisialisasi isAsking

    messages = []
    tf = ft.TextField(value='', expand=True, 
                      autofocus=True, shift_enter=True,
                      bgcolor=ft.colors.GREY_700, icon=ft.icons.WECHAT_OUTLINED)
    lf = ft.ListView(controls=messages, auto_scroll=False, expand=True, reverse=True)
    btt = ft.IconButton(icon=ft.icons.SEND_OUTLINED)

    def getMD(mdtxt):
        return ft.Markdown(
            mdtxt,
            selectable=True,
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"),
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: page.launch_url(e.data),
        )

    def show_bertscore_ui(precision, recall, f1_score):
        # Fungsi untuk menampilkan UI BERTScore
        score_box = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(f"Precision: {precision:.4f}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.GREEN_400,
                    padding=10,
                    border_radius=5,
                    margin=5
                ),
                ft.Container(
                    content=ft.Text(f"Recall: {recall:.4f}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.BLUE_400,
                    padding=10,
                    border_radius=5,
                    margin=5
                ),
                ft.Container(
                    content=ft.Text(f"F1 Score: {f1_score:.4f}", color=ft.colors.WHITE),
                    bgcolor=ft.colors.RED_400,
                    padding=10,
                    border_radius=5,
                    margin=5
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        page.overlay.append(score_box)
        page.update()

    def ask(e):
        global isAsking
        if isAsking:
            return
        
        question = tf.value.strip()  # Menghilangkan spasi ekstra di sekitar teks
        if not question:  # Memastikan tidak mengirim pesan jika pertanyaan kosong
            return
        
        isAsking = True
        btt.disabled = True
        response_text = ''  # Initialize response_text to avoid the error

        tf.value = ''  # Mengosongkan nilai TextField setelah mengirim pertanyaan
        mdQuestion = getMD(question)

        messages.insert(0, ft.Card(
            content=ft.Container(padding=5, content=mdQuestion), 
            color=ft.colors.BLUE_400, margin=ft.Margin(left=10, right=0, top=5, bottom=5)))
        
        try: 
            if "yesus" in question.lower():
                response_text = chat.send_message(question).text
                responseText = filter_yesus(response_text)
            else:
                responseText = "Maaf, saya hanya memberikan informasi tentang Yesus."
            
            # Hitung BERTScore untuk respons yang dihasilkan
            precision, recall, f1_score = compute_bertscore(responseText, question)
            
            mdTxt = getMD(responseText)  # Use responseText instead of response_text
            messages.insert(0, ft.Card(
                content=ft.Container(padding=5, content=mdTxt),
                color=ft.colors.GREY_700, margin=ft.Margin(left=0, right=10, top=5, bottom=5)))
            
            lf.scroll_to(0.0, duration=500)
            page.update()
            
            # Tampilkan UI BERTScore
            show_bertscore_ui(precision, recall, f1_score)

        except Exception as e:
            mdTxt = getMD(str(e))
            messages.insert(0, ft.Card(
                content=ft.Container(padding=5, content=mdTxt),
                color=ft.colors.GREY_700, margin=ft.Margin(left=0, right=10, top=5, bottom=5)))
            page.update()
        
        btt.disabled = False
        page.update()
        isAsking = False

    btt.on_click = ask
    tf.on_submit = ask
    container = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                lf,
                ft.Row(
                    controls=[
                        tf,
                        btt
                    ]
                )
            ]
        )
    )

    page.add(container)

ft.app(main)
