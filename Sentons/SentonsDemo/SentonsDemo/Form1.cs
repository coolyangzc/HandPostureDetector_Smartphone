using System;
using System.Diagnostics;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;

namespace SentonsDemo
{
    public partial class Form1 : Form
    {
        private const Boolean runPython = true;

        private SentonsReader reader;
        private TouchReader.TouchSet newestTouchset;
        private HistoryValueContainer LR = new HistoryValueContainer(1500, 0.01);
        private Thread classifierThread = new Thread(RunClassifier);

        const int UP_MM = 116;
        const int UP_PIXEL = 100;
        const int DOWN_PIXEL = 740;
        const int LEFT_PIXEL = 400;
        const int RIGHT_PIXEL = 760;

        public Form1()
        {
            InitializeComponent();
            SetStyle(ControlStyles.UserPaint, true);
            SetStyle(ControlStyles.AllPaintingInWmPaint, true);
            SetStyle(ControlStyles.OptimizedDoubleBuffer, true);
            reader = new SentonsReader(this);
            reader.connect();
            reader.startRead();
            classifierThread.Start();
        }

        static void RunClassifier()
        {
            if (runPython)
                RunCmd("python run.py");
        }

        static string RunCmd(string command)
        {
            Process p = new Process();
            p.StartInfo.FileName = "cmd.exe";         
            p.StartInfo.Arguments = "/c " + command;
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardInput = true;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardError = true;  
            p.StartInfo.CreateNoWindow = true;
            p.Start();
            return p.StandardOutput.ReadToEnd();
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
            g.DrawString(Math.Round(LR.value, 2).ToString(), font, blackBrush, 100, 700);
            if (LR.value < -0.5)
                resultPic.Image = Image.FromFile("v_l.png");
            else if (LR.value > 0.5)
                resultPic.Image = Image.FromFile("v_r.png");
            else
                resultPic.Image = null;
            
            if (newestTouchset == null)
                return;
            int x;
            for (int i = 0; i < newestTouchset.touchList.Count; i++)
            {
                TouchReader.TouchReport entry = newestTouchset.touchList[i];
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

        public void Update(TouchReader.TouchSet newestTouchset, double result = 0)
        {
            this.newestTouchset = newestTouchset;
            LR.Update(result, DateTime.Now);
            this.Invalidate();
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            reader.finishRead();
            reader.disconnect();
            classifierThread.Abort();
        }
    }
}
