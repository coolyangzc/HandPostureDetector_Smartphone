using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SentonsDemo
{
    public partial class Form1 : Form
    {
        private SentonsReader reader;
        public Form1()
        {
            InitializeComponent();
            reader = new SentonsReader(this);
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void connectBtn_Click(object sender, EventArgs e)
        {
            reader.connect();
            reader.startRead();
        }

        private void disconnectBtn_Click(object sender, EventArgs e)
        {
            reader.finishRead();
            reader.disconnect();
        }

        private void Form1_Paint(object sender, PaintEventArgs e)
        {
        }

    }
}
