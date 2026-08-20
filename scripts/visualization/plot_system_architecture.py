"""Generate a clean, compact, minimalist System Architecture Diagram for PPT.

Outputs saved to:
    artifacts/figures/system_architecture_compact.png
    artifacts/figures/system_architecture_diagram.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = Path("artifacts/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUTPUT_DIR / "system_architecture_compact.png"
OUT_PATH_MAIN = OUTPUT_DIR / "system_architecture_diagram.png"


def draw_compact_architecture():
    fig, ax = plt.subplots(figsize=(10, 11), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis("off")

    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    def draw_box(x, y, w, h, bg, border, title, items=None, radius=0.12):
        box = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.04,rounding_size={radius}",
            facecolor=bg, edgecolor=border, linewidth=1.5
        )
        ax.add_patch(box)
        if title:
            ax.text(x + w / 2, y + h - 0.28, title, ha="center", va="center", fontsize=11, fontweight="bold", color="#0f172a")
        if items:
            start_y = y + h - 0.58
            for i, it in enumerate(items):
                ax.text(x + w / 2, start_y - i * 0.3, it, ha="center", va="center", fontsize=9.2, color="#334155")

    def draw_badge(x, y, text, bg="#e2e8f0", text_color="#1e293b", fontsize=8):
        ax.text(
            x, y, text,
            ha="center", va="center",
            fontsize=fontsize, fontweight="600", color=text_color,
            bbox=dict(boxstyle="round,pad=0.2,rounding_size=0.08", facecolor=bg, edgecolor="#cbd5e1", lw=0.7)
        )

    # Title
    ax.text(5.0, 10.6, "KIẾN TRÚC TỔNG THỂ HỆ THỐNG STUDYDRIVE & ML", ha="center", va="center", fontsize=13, fontweight="bold", color="#0f172a")

    # 1. TOP: ML Pipeline
    draw_box(2.2, 8.4, 5.6, 1.8, "#faf5ff", "#a855f7", "ML Detection Pipeline", [
        "1. Time Window (5 phút)",
        "2. Feature Engineering (25 đặc trưng)",
        "3. Isolation Forest (Phát hiện bất thường)"
    ])

    # 2. CENTER: Database
    draw_box(3.0, 5.4, 4.0, 1.8, "#fffbeb", "#f59e0b", "Database (SQLite / MySQL)", [
        "• Users & Files Metadata",
        "• RequestLogs (27 thuộc tính)",
        "• Alerts (Cảnh báo)"
    ])

    # Connectors between ML & DB
    ax.annotate("", xy=(5.8, 8.4), xytext=(5.8, 7.2), arrowprops=dict(arrowstyle="-|>", color="#2563eb", lw=1.8, mutation_scale=12))
    draw_badge(6.8, 7.8, "Đọc Logs", bg="#dbeafe", text_color="#1d4ed8")

    ax.annotate("", xy=(4.2, 7.2), xytext=(4.2, 8.4), arrowprops=dict(arrowstyle="-|>", color="#dc2626", lw=1.8, mutation_scale=12))
    draw_badge(3.2, 7.8, "Alerts & Khóa User", bg="#fee2e2", text_color="#b91c1c")

    # 3. LEFT: Admin & User
    draw_box(0.4, 5.5, 2.0, 1.6, "#eff6ff", "#3b82f6", "Admin Dashboard", ["• Xem Cảnh báo", "• Giám sát Logs"])
    draw_box(0.4, 3.2, 2.0, 1.4, "#f0fdf4", "#22c55e", "Users / Clients", ["• Người dùng thật", "• Simulators"])

    # Connectors Left Flow
    ax.annotate("", xy=(2.4, 6.3), xytext=(3.0, 6.3), arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.5, mutation_scale=10))
    ax.annotate("", xy=(1.4, 4.6), xytext=(1.4, 5.5), arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.5, linestyle="--"))
    ax.annotate("", xy=(2.4, 3.9), xytext=(3.0, 3.9), arrowprops=dict(arrowstyle="<-", color="#0284c7", lw=1.8, mutation_scale=12))
    draw_badge(2.0, 2.8, "HTTP Requests", bg="#e0f2fe", text_color="#0369a1")

    # 4. BOTTOM: Flask Web App
    draw_box(3.0, 2.0, 6.5, 2.4, "#f8fafc", "#475569", "STUDYDRIVE — Flask Web Layer", [
        "• Routes, Authentication & Authorization (RBAC)",
        "• Quản lý tài liệu (Upload, Download, Share, Delete)",
        "• Structured Logging Middleware (Ghi 27 trường log)"
    ])

    # Connectors App -> DB
    ax.annotate("", xy=(5.0, 5.4), xytext=(5.0, 4.4), arrowprops=dict(arrowstyle="-|>", color="#16a34a", lw=1.8, mutation_scale=12))
    draw_badge(5.0, 4.9, "Lưu Metadata & RequestLogs", bg="#dcfce7", text_color="#15803d")

    # 5. STORAGE
    draw_box(4.2, 0.4, 4.2, 0.9, "#f1f5f9", "#94a3b8", "File Storage (Physical)", ["Thư mục: instance/uploads/{UUID}"])
    ax.annotate("", xy=(6.3, 1.3), xytext=(6.3, 2.0), arrowprops=dict(arrowstyle="-|>", color="#64748b", lw=1.5, mutation_scale=10))
    draw_badge(6.3, 1.65, "Lưu file vật lý", bg="#ffffff", fontsize=7.5)

    plt.tight_layout()
    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    fig.savefig(OUT_PATH_MAIN, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f" Saved compact architecture to: {OUT_PATH}")


if __name__ == "__main__":
    draw_compact_architecture()
