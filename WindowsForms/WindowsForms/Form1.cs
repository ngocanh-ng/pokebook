using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using MySql.Data.MySqlClient;

namespace WindowsForms
{
    public partial class Pokebook : Form
    {

        public Pokebook()
        {
            InitializeComponent();
            this.Load += Pokebook_Load;
        }

        private void Pokebook_Load(object sender, EventArgs e)
        {
            ShowAllCardImages();
        }

        private string imagesFolderPath = @"C:\Users\Ngoc Anh\source\repos\pokebook\assets\Karten_Bilder";

        private void ShowAllCardImages(string nameFilter = null)
        {
            DataTable cards = GetCardImageNamesFromDB(nameFilter);

            flowLayoutPanelCards.Controls.Clear();

            foreach (DataRow row in cards.Rows)
            {
                string imageName = row["Bildname"].ToString();

                PictureBox pic = new PictureBox();
                pic.Width = 140;
                pic.Height = 190;
                pic.SizeMode = PictureBoxSizeMode.Zoom;
                pic.Margin = new Padding(5);

                string imgPath = System.IO.Path.Combine(imagesFolderPath, imageName);
                if (System.IO.File.Exists(imgPath))
                {
                    using (var temp = Image.FromFile(imgPath))
                    {
                        pic.Image = new Bitmap(temp);
                    }
                }

                flowLayoutPanelCards.Controls.Add(pic);
            }
        }


        private DataTable GetAllCardImageNamesFromDB()
        {
            string connStr = "server=127.0.0.1;database=team02;uid=na_ng;pwd=botanical;";
            string query = "SELECT DISTINCT Bildname FROM karte ORDER BY Bildname ASC";

            DataTable dt = new DataTable();

            try
            {
                using (MySqlConnection conn = new MySqlConnection(connStr))
                {
                    conn.Open();
                    using (MySqlCommand cmd = new MySqlCommand(query, conn))
                    using (MySqlDataAdapter adapter = new MySqlDataAdapter(cmd))
                    {
                        adapter.Fill(dt);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("DB Fehler: " + ex.Message);
            }

            return dt;
        }
        private DataTable GetCardImageNamesFromDB(string nameFilter = null)
        {
            string connStr = "server=127.0.0.1;database=team02;uid=na_ng;pwd=botanical;";
            string query = "SELECT DISTINCT Bildname FROM karte";

            if (!string.IsNullOrEmpty(nameFilter))
            {
                query += " WHERE Name LIKE @nameFilter";
            }

            query += " ORDER BY Bildname ASC";

            DataTable dt = new DataTable();

            try
            {
                using (MySqlConnection conn = new MySqlConnection(connStr))
                {
                    conn.Open();
                    using (MySqlCommand cmd = new MySqlCommand(query, conn))
                    {
                        if (!string.IsNullOrEmpty(nameFilter))
                        {
                            cmd.Parameters.AddWithValue("@nameFilter", nameFilter + "%");
                        }

                        using (MySqlDataAdapter adapter = new MySqlDataAdapter(cmd))
                        {
                            adapter.Fill(dt);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("DB Fehler: " + ex.Message);
            }

            return dt;
        }

        private void tb_name_TextChanged(object sender, EventArgs e)
        {
            string searchTerm = tb_name.Text.Trim();
            ShowAllCardImages(searchTerm);
        }
    }

}
