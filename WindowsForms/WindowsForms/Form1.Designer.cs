namespace WindowsForms
{
    partial class Pokebook
    {
        /// <summary>
        /// Erforderliche Designervariable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Verwendete Ressourcen bereinigen.
        /// </summary>
        /// <param name="disposing">True, wenn verwaltete Ressourcen gelöscht werden sollen; andernfalls False.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Vom Windows Form-Designer generierter Code

        /// <summary>
        /// Erforderliche Methode für die Designerunterstützung.
        /// Der Inhalt der Methode darf nicht mit dem Code-Editor geändert werden.
        /// </summary>
        private void InitializeComponent()
        {
            this.flowLayoutPanelCards = new System.Windows.Forms.FlowLayoutPanel();
            this.tb_name = new System.Windows.Forms.TextBox();
            this.lb_name = new System.Windows.Forms.Label();
            this.SuspendLayout();
            // 
            // flowLayoutPanelCards
            // 
            this.flowLayoutPanelCards.AutoScroll = true;
            this.flowLayoutPanelCards.Dock = System.Windows.Forms.DockStyle.Right;
            this.flowLayoutPanelCards.Location = new System.Drawing.Point(340, 0);
            this.flowLayoutPanelCards.Name = "flowLayoutPanelCards";
            this.flowLayoutPanelCards.Size = new System.Drawing.Size(882, 772);
            this.flowLayoutPanelCards.TabIndex = 0;
            // 
            // tb_name
            // 
            this.tb_name.Location = new System.Drawing.Point(115, 55);
            this.tb_name.Name = "tb_name";
            this.tb_name.Size = new System.Drawing.Size(160, 31);
            this.tb_name.TabIndex = 1;
            this.tb_name.TextChanged += new System.EventHandler(this.tb_name_TextChanged);
            // 
            // lb_name
            // 
            this.lb_name.AutoSize = true;
            this.lb_name.Location = new System.Drawing.Point(35, 58);
            this.lb_name.Name = "lb_name";
            this.lb_name.Size = new System.Drawing.Size(74, 25);
            this.lb_name.TabIndex = 2;
            this.lb_name.Text = "Name:";
            // 
            // Pokebook
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(12F, 25F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1222, 772);
            this.Controls.Add(this.lb_name);
            this.Controls.Add(this.tb_name);
            this.Controls.Add(this.flowLayoutPanelCards);
            this.Name = "Pokebook";
            this.Text = "Pokebook";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.FlowLayoutPanel flowLayoutPanelCards;
        private System.Windows.Forms.TextBox tb_name;
        private System.Windows.Forms.Label lb_name;
    }
}

