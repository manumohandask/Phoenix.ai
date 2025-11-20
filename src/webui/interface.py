import gradio as gr
import base64
from pathlib import Path

from src.webui.webui_manager import WebuiManager
from src.webui.components.agent_settings_tab import create_agent_settings_tab
from src.webui.components.browser_settings_tab import create_browser_settings_tab
from src.webui.components.browser_use_agent_tab import create_browser_use_agent_tab
from src.webui.components.deep_research_agent_tab import create_deep_research_agent_tab
from src.webui.components.pr_testing_agent_tab import create_pr_testing_agent_tab
from src.webui.components.load_save_config_tab import create_load_save_config_tab

theme_map = {
    "Default": gr.themes.Default(),
    "Soft": gr.themes.Soft(),
    "Monochrome": gr.themes.Monochrome(),
    "Glass": gr.themes.Glass(),
    "Origin": gr.themes.Origin(),
    "Citrus": gr.themes.Citrus(),
    "Ocean": gr.themes.Ocean(),
    "Base": gr.themes.Base()
}


def create_ui(theme_name="Ocean"):
    css = """
    /* Clean Dark Professional Theme */
    .gradio-container {
        width: 90vw !important; 
        max-width: 1600px !important; 
        margin: 0 auto !important;
        padding: 30px !important;
        background: #0d1117 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Header Container */
    .header-row {
        background: linear-gradient(135deg, #1a1f28 0%, #0d1117 100%) !important;
        padding: 25px 50px !important;
        border-radius: 16px !important;
        margin-bottom: 30px !important;
        border: 1px solid rgba(255, 193, 7, 0.15) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Logo Hover Effect */
    .phoenix-logo-hover:hover {
        transform: translateY(-5px) scale(1.1) rotate(8deg) !important;
        filter: drop-shadow(0 0 30px rgba(255, 106, 0, 0.9)) drop-shadow(0 12px 25px rgba(255, 140, 0, 0.6)) !important;
    }
    
    /* Logo Styling - No animations, no download icon */
    .phoenix-logo-img {
        border-radius: 8px !important;
        max-width: 120px !important;
        flex-shrink: 0 !important;
    }
    
    .phoenix-logo-img img {
        width: 100px !important;
        height: 100px !important;
        object-fit: contain !important;
        border-radius: 8px !important;
        display: block !important;
    }
    
    /* Hide download button completely */
    .phoenix-logo-img button,
    .phoenix-logo-img .download-button {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    
    /* Header Text Styling */
    .phoenix-header-text {
        padding: 0 !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    .phoenix-title {
        font-size: 2.5em !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin: 0 0 10px 0 !important;
        letter-spacing: 1px !important;
    }
    
    .phoenix-subtitle {
        font-size: 1.1em !important;
        color: #8b949e !important;
        margin: 0 0 20px 0 !important;
        font-weight: 400 !important;
    }
    
    /* Feature Badges */
    .phoenix-badges {
        display: flex !important;
        gap: 10px !important;
        flex-wrap: wrap !important;
    }
    
    .phoenix-badge {
        background: #21262d !important;
        color: #ffffff !important;
        padding: 8px 18px !important;
        border-radius: 20px !important;
        font-size: 0.9em !important;
        font-weight: 500 !important;
        border: 1px solid #30363d !important;
    }
    
    /* Tab Styling - Dark Theme */
    .tabs button {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        margin: 0 5px !important;
        transition: all 0.2s ease !important;
        color: #8b949e !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
    }
    
    .tabs button:hover {
        background: #30363d !important;
        border-color: #484f58 !important;
        color: #ffffff !important;
    }
    
    .tabs button.selected {
        background: #ff6b35 !important;
        border-color: #ff6b35 !important;
        color: #ffffff !important;
    }
    
    /* Button Styling - Dark Theme */
    button {
        background: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
    }
    
    button:hover {
        background: #30363d !important;
        border-color: #484f58 !important;
    }
    
    /* Input Field Styling - Dark Theme */
    input, textarea, select {
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        background: #0d1117 !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: #ff6b35 !important;
        box-shadow: 0 0 0 3px rgba(44, 62, 80, 0.1) !important;
        outline: none !important;
    }
    
    /* Status Messages */
    .success-message {
        color: #16a34a !important;
        background: #f0fdf4 !important;
        border-left: 4px solid #16a34a !important;
        padding: 12px !important;
        border-radius: 6px !important;
    }
    
    .error-message {
        color: #dc2626 !important;
        background: #fef2f2 !important;
        border-left: 4px solid #dc2626 !important;
        padding: 10px !important;
        border-radius: 5px !important;
    }
    """

    # Light mode with professional grey theme
    js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') === 'dark') {
            url.searchParams.delete('__theme');
            window.location.href = url.href;
        }
    }
    """

    ui_manager = WebuiManager()

    # Phoenix AI Theme - Clean Dark
    phoenix_theme = gr.themes.Base(
        primary_hue=gr.themes.colors.slate,
        secondary_hue=gr.themes.colors.gray,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont('Inter'), 'ui-sans-serif', 'system-ui', 'sans-serif'],
    ).set(
        # Button styling
        button_primary_background_fill='#ff6b35',
        button_primary_background_fill_hover='#ff5722',
        button_primary_text_color='#ffffff',
        button_secondary_background_fill='#21262d',
        button_secondary_background_fill_hover='#30363d',
        button_secondary_text_color='#ffffff',
        
        # Text colors - Dark theme
        block_label_text_color='#8b949e',
        block_title_text_color='#ffffff',
        body_text_color='#ffffff',
        
        # Background colors - Dark
        background_fill_primary='#0d1117',
        background_fill_secondary='#161b22',
        block_background_fill='#161b22',
        
        # Border colors
        block_border_color='#30363d',
        block_border_width='1px',
        block_radius='8px',
        
        # Input styling - Dark
        input_background_fill='#0d1117',
        input_border_color='#30363d',
        input_border_width='1px',
        input_radius='6px',
    )

    with gr.Blocks(
            title="Phoenix AI - Intelligent Testing Platform", 
            theme=phoenix_theme if theme_name == "Ocean" else theme_map[theme_name], 
            css=css, 
            js=js_func,
    ) as demo:
        # Phoenix Header - Clean and Simple
        # Load and encode logo image
        logo_path = Path("assets/phoenix-logo.png")
        logo_base64 = ""
        if logo_path.exists():
            with open(logo_path, "rb") as img_file:
                logo_base64 = base64.b64encode(img_file.read()).decode()
        
        with gr.Row(elem_classes="header-row"):
            gr.HTML(
                f"""
                <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Orbitron:wght@500&display=swap" rel="stylesheet">
                <div style="display: flex; align-items: center; justify-content: center; gap: 40px; width: 100%; padding: 5px 0;">
                    <img src="data:image/png;base64,{logo_base64}" 
                         class="phoenix-logo-hover"
                         style="width: 125px; height: 125px; object-fit: contain; border-radius: 12px; flex-shrink: 0; transition: all 0.3s ease; filter: drop-shadow(0 0 20px rgba(255, 106, 0, 0.6)) drop-shadow(0 8px 16px rgba(255, 140, 0, 0.4));">
                    <div style="text-align: center; flex: 0 1 auto;">
                        <h1 style="
                            font-family: 'Montserrat', sans-serif;
                            font-weight: 800;
                            font-size: 52px;
                            background: linear-gradient(135deg, #FFD700 0%, #FF8C00 50%, #FF0000 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                            line-height: 110%;
                            letter-spacing: 2px;
                            text-transform: uppercase;
                            margin: 0 0 12px 0;
                            filter: drop-shadow(0 0 30px rgba(255, 215, 0, 0.4)) drop-shadow(0 5px 20px rgba(255, 106, 0, 0.5)) drop-shadow(0 8px 25px rgba(255, 0, 0, 0.3));
                        ">PHOENIX AI</h1>
                        <p style="
                            font-family: 'Orbitron', sans-serif;
                            font-weight: 500;
                            font-size: 19px;
                            color: #FFC107;
                            line-height: 140%;
                            letter-spacing: 1px;
                            margin: 0;
                            text-shadow: 0 2px 10px rgba(255, 193, 7, 0.3);
                        ">Intelligent E2E Testing & Automation Platform</p>
                    </div>
                </div>
                """
            )

        with gr.Tabs() as tabs:
            with gr.TabItem("⚙️ Agent Settings"):
                create_agent_settings_tab(ui_manager)

            with gr.TabItem("🌐 Browser Settings"):
                create_browser_settings_tab(ui_manager)

            with gr.TabItem("🤖 Browser Automation"):
                create_browser_use_agent_tab(ui_manager)

            with gr.TabItem("🔍 PR Testing"):
                create_pr_testing_agent_tab(ui_manager)

            with gr.TabItem("� Testing Suite"):
                gr.Markdown(
                    """
                    ### Phoenix AI Testing Capabilities
                    """,
                    elem_classes=["tab-header-text"],
                )
                with gr.Tabs():
                    with gr.TabItem("🔬 Deep Research"):
                        create_deep_research_agent_tab(ui_manager)

            with gr.TabItem("📁 Load & Save Config"):
                create_load_save_config_tab(ui_manager)

    return demo
