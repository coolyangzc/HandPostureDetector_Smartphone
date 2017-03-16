using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsApplication
{
    class Program
    {
        static void Main(string[] args)
        {
            SentonsReader reader = new SentonsReader();
            reader.connect();
            reader.startRead();
            while (true) ;
            //reader.setWriter((StreamWriter)Console.Out);
        }
    }
}
