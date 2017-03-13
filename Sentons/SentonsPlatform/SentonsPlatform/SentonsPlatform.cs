using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsPlatform
{
    class SentonsPlatform
    {
        string userPath, expPath;
        string userName;
        List<string> missions = new List<string>();
        int expID = 0;
        StreamReader reader;
        StreamWriter writer;
        SentonsReader sReader = new SentonsReader();
        public SentonsPlatform(string userPath, string expPath)
        {
            this.userPath = userPath;
            this.expPath = expPath;
        }
        public void ReadUserInfo()
        {
            using (StreamReader reader = new StreamReader(File.Open(userPath, FileMode.Open)))
            {
                userName = reader.ReadLine();
                Console.WriteLine("UserName:" + userName);
            }
        }
        public void Run()
        {
            ReadUserInfo();
            reader = new StreamReader(File.Open(expPath, FileMode.Open));
            if (!Directory.Exists(userName))
                Directory.CreateDirectory(userName);

            string mission = string.Empty;
            while(true)
            {
                mission = reader.ReadLine();
                if (mission == null)
                    break;
                missions.Add(mission);
            }
            reader.Close();
            expID = 0;
            while(expID < missions.Count)
            {
                RunMission(missions[expID]);
            }
            Console.Clear();
            Console.WriteLine("实验结束！感谢您的协作与配合！");
            Console.ReadKey();
        }

        void RunMission(string mission)
        {
            string[] components = mission.Split(' ');
            string fileName = userName + "/" + components[0] + ".txt";

            Console.Clear();
            Console.WriteLine("实验" + components[0] + '\n');
            Console.WriteLine(components[2]);
            Console.WriteLine(components[3]);
            Console.Write("\n请输入指令(P:前一任务 任意:开始任务):");
            string cmd = Console.ReadLine();
            if (cmd.Length > 0 && (cmd[0] == 'P' || cmd[0] == 'p'))
            {
                if (expID > 0)
                    expID--;
                return;
            }
            Console.Write("\n实验开始\n...\n");
            writer = new StreamWriter(File.Open(fileName, FileMode.Create));
            writer.WriteLine(components[1]);
            writer.WriteLine(components[2]);
            writer.WriteLine(components[3]);
            sReader.connect();
            sReader.setWriter(writer);
            sReader.startRecord();
            Console.Write("\n请输入指令(R:重做任务 任意:下一任务):");
            cmd = Console.ReadLine();
            sReader.finishRecord();
            sReader.disconnect();
            writer.Close();
            if (cmd.Length > 0 && (cmd[0] == 'R' || cmd[0] == 'r'))
                return;
            expID++;
            
        }
    }
}
