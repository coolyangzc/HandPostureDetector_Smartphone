using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;



namespace SentonsReader
{
    class Program
    {
        static void Main(string[] args)
        {
            SentonsReader reader = new SentonsReader();

            reader.connect();
            while (true)
            {
                reader.read();
                System.Console.Write("--------------------------------------------------\n");
                //System.Threading.Thread.Sleep(1000);
            }
            //reader.disconnect();

        }
    }
}
