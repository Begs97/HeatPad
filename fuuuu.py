from tkinter import Frame, Tk, BOTH, Text, Menu, END

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)   

        self.parent = parent        
        self.initUI()
       
            
def main():

    root = Tk()
    ex = Example(root)
    root.minsize(320, 240)
    root.mainloop()  
    
if __name__ == '__main__':
    main()
