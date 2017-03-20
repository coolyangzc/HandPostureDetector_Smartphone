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
        private TouchReader.TouchSet newestTouchset;
        private HistoryValueContainer LR = new HistoryValueContainer(2000, 0.01);

        const int UP_MM = 116;
        const int UP_PIXEL = 100;
        const int DOWN_PIXEL = 740;
        const int LEFT_PIXEL = 620;
        const int RIGHT_PIXEL = 980;

        public Form1()
        {
            InitializeComponent();
            SetStyle(ControlStyles.UserPaint, true);
            SetStyle(ControlStyles.AllPaintingInWmPaint, true);
            SetStyle(ControlStyles.OptimizedDoubleBuffer, true);
            reader = new SentonsReader(this);
            reader.connect();
            reader.startRead();
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void Form1_Paint(object sender, PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            Pen pen = new Pen(Color.Black, 2);
            g.DrawRectangle(pen, LEFT_PIXEL, UP_PIXEL, RIGHT_PIXEL - LEFT_PIXEL, DOWN_PIXEL - UP_PIXEL);
            Font font = new Font("Times New Roman", 20);
            Brush blackBrush = new SolidBrush(Color.Black);
            g.DrawString(Math.Round(LR.value, 2).ToString(), font, blackBrush, 100, 100);
            if (newestTouchset == null)
                return;
            int x;
            foreach (TouchReader.TouchReport entry in newestTouchset.touchList)
            {
                if (entry.BarID == 0)
                    x = RIGHT_PIXEL;
                else
                    x = LEFT_PIXEL;
                float posU = SentonsReader.processSignedDiv16(entry.pos1);
                float posD = SentonsReader.processSignedDiv16(entry.pos2);
                posU = (1 - posU / UP_MM) * (DOWN_PIXEL - UP_PIXEL) + UP_PIXEL;
                posD = (1 - posD / UP_MM) * (DOWN_PIXEL - UP_PIXEL) + UP_PIXEL;
                pen = new Pen(Color.FromArgb(Math.Min(entry.force_lvl * 5, 255), 0, Math.Max(255 - entry.force_lvl * 5, 0)), 5);
                g.DrawLine(pen, x, posU, x, posD);
            }
        }

        public void update(TouchReader.TouchSet newestTouchset, double result = 0)
        {
            this.newestTouchset = newestTouchset;
            LR.update(result, DateTime.Now);
            this.Invalidate();
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            reader.finishRead();
            reader.disconnect();
        }
    }
}
