package Get_Phone;
import javax.swing.*;
import java.awt.event.*;
import java.net.URLEncoder;
import Get_Phone.HttpRequest.*;

public class Get_Phone
{
    public static void main(String[] args)
    {
        JFrame frame_main = new JFrame("Get_Phone");
        JPanel panel_main = new JPanel();
        JButton button_confirm = new JButton(" 确定 ");
        JTextArea textarea_info = new JTextArea();
        JTextArea textarea_key = new JTextArea("请输入你的密钥");
        JTextArea textarea_name = new JTextArea("请输入要查询的id");
        JTextArea textarea_city = new JTextArea("请输入号码归属地");

        panel_main.setLayout(null);

        frame_main.setBounds(0, 0, 500, 500);
        panel_main.setBounds(0, 0, 500, 500);
        button_confirm.setBounds(400, 350, 50, 50);
        textarea_city.setBounds(100, 410, 200, 30);
        textarea_name.setBounds(100, 370, 200, 30);
        textarea_key.setBounds(100, 330, 200, 30);
        textarea_info.setBounds(50, 100, 400, 200);

        textarea_info.setLineWrap(true);

        textarea_city.addFocusListener(new MyKey(textarea_city, 3));
        textarea_name.addFocusListener(new MyKey(textarea_name, 2));
        textarea_key.addFocusListener(new MyKey(textarea_key, 1));
        button_confirm.addActionListener(new MyButton(textarea_info, textarea_key, textarea_name, textarea_city));
        frame_main.addWindowListener(new MyFrame());

        panel_main.add(textarea_city);
        panel_main.add(textarea_name);
        panel_main.add(textarea_key);
        panel_main.add(textarea_info);
        panel_main.add(button_confirm);
        frame_main.add(panel_main);
        frame_main.setVisible(true);
    }
}

class MyFrame implements WindowListener {

    @Override
    public void windowOpened(WindowEvent e) {

    }

    @Override
    public void windowClosing(WindowEvent e) {
        System.exit(0);
    }

    @Override
    public void windowClosed(WindowEvent e) {
        System.exit(0);
    }

    @Override
    public void windowIconified(WindowEvent e) {

    }

    @Override
    public void windowDeiconified(WindowEvent e) {

    }

    @Override
    public void windowActivated(WindowEvent e) {

    }

    @Override
    public void windowDeactivated(WindowEvent e) {

    }
}

class MyButton implements ActionListener
{
    JTextArea info;
    JTextArea key;
    JTextArea name;
    JTextArea city;
    public MyButton(JTextArea info, JTextArea key, JTextArea name, JTextArea city)
    {
        this.info = info;
        this.key = key;
        this.name = name;
        this.city = city;
    }
    @Override
    public void actionPerformed(ActionEvent e)
    {
        String url = null;
        try {
            if(this.city.getText().equals("请输入号码归属地"))
            {
                //System.out.print(this.name.getText());
                url = String.format("http://114.215.92.93/info/%s/%s", this.key.getText(), URLEncoder.encode(this.name.getText(), "UTF-8"));
            }
            else
            {
                url = String.format("http://114.215.92.93/info/%s/%s/%s", this.key.getText(), URLEncoder.encode(this.name.getText(), "UTF-8"), URLEncoder.encode(this.city.getText(), "UTF-8"));
            }
            System.out.print(url);
            String respond = HttpRequest.sendGet(url, "");
            this.info.setText(respond);
        } catch(Exception e1) {
            //System.out.print("error");
            this.info.setText("error");
        }
        finally {
            this.info.setText(this.info.getText() + "\n查询完成");
        }
    }
}

class MyKey implements FocusListener
{
    JTextArea key;
    int choose;
    String init_str;
    public MyKey(JTextArea key, int choose)
    {
        this.key = key;
        this.choose = choose;
        this.init_str = key.getText();
    }
    @Override
    public void focusGained(FocusEvent e) {
        if(this.key.getText().equals(this.init_str)) {
            this.key.setText("");
        }
    }

    @Override
    public void focusLost(FocusEvent e) {
        if(this.key.getText().equals(""))
        {
            if(this.choose == 1)
            {
                this.key.setText("请输入你的密钥");
            }
            else if(this.choose == 2)
            {
                this.key.setText("请输入要查询的id");
            }
            else if(this.choose == 3)
            {
                this.key.setText("请输入号码归属地");
            }
        }
    }
}